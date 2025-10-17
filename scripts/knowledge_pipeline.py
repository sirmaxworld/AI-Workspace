#!/usr/bin/env python3
"""Autonomous knowledge pipeline for multi-source curation."""

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

from data_collection_crew import DataCollectionCrew, OutputValidationError

try:  # Optional dependency
    from jsonschema import Draft7Validator, ValidationError

    JSONVALIDATOR_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback when jsonschema missing
    JSONVALIDATOR_AVAILABLE = False
    Draft7Validator = None  # type: ignore
    ValidationError = Exception  # type: ignore

try:  # Optional dependency
    from mem0 import Memory

    MEM0_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback when mem0 missing
    MEM0_AVAILABLE = False
    Memory = None  # type: ignore


load_dotenv('/Users/yourox/AI-Workspace/.env')

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=os.getenv('KNOWLEDGE_PIPELINE_LOG_LEVEL', 'INFO'))


BASE_PATH = Path('/Users/yourox/AI-Workspace')
DATA_PATH = BASE_PATH / 'data'


class StructuredOutputValidator:
    """Validate and normalise structured outputs from crews."""

    def __init__(self) -> None:
        self.schemas: Dict[str, Dict[str, Any]] = {
            'youtube': {
                'type': 'object',
                'required': ['videos', 'summary'],
                'properties': {
                    'videos': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'required': ['url', 'title', 'channel'],
                            'properties': {
                                'url': {'type': 'string'},
                                'title': {'type': 'string'},
                                'channel': {'type': 'string'},
                                'published': {'type': 'string'},
                                'summary': {'type': 'string'},
                                'relevance': {'type': ['number', 'string']},
                            },
                        },
                    },
                    'summary': {'type': ['string', 'array']},
                    'notes': {'type': ['string', 'array']},
                },
            },
            'academic': {
                'type': 'object',
                'required': ['papers', 'insights'],
                'properties': {
                    'papers': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'required': ['title', 'url', 'summary'],
                            'properties': {
                                'title': {'type': 'string'},
                                'url': {'type': 'string'},
                                'authors': {'type': 'array', 'items': {'type': 'string'}},
                                'summary': {'type': 'string'},
                                'source': {'type': 'string'},
                                'published': {'type': 'string'},
                            },
                        },
                    },
                    'insights': {'type': 'array', 'items': {'type': 'string'}},
                },
            },
            'social': {
                'type': 'object',
                'required': ['posts', 'trends'],
                'properties': {
                    'posts': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'required': ['source', 'url', 'title', 'sentiment'],
                            'properties': {
                                'source': {'type': 'string'},
                                'url': {'type': 'string'},
                                'title': {'type': 'string'},
                                'summary': {'type': 'string'},
                                'sentiment': {'type': 'string'},
                            },
                        },
                    },
                    'trends': {'type': 'array', 'items': {'type': 'string'}},
                    'warnings': {'type': 'array', 'items': {'type': 'string'}},
                },
            },
            'industry': {
                'type': 'object',
                'required': ['articles', 'highlights'],
                'properties': {
                    'articles': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'required': ['title', 'url', 'summary'],
                            'properties': {
                                'title': {'type': 'string'},
                                'url': {'type': 'string'},
                                'publisher': {'type': 'string'},
                                'summary': {'type': 'string'},
                                'impact': {'type': 'string'},
                            },
                        },
                    },
                    'highlights': {'type': 'array', 'items': {'type': 'string'}},
                },
            },
            'synthesizer': {
                'type': 'object',
                'required': ['knowledge_base', 'topic_map'],
                'properties': {
                    'knowledge_base': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'required': ['title', 'content', 'source_type'],
                            'properties': {
                                'id': {'type': 'string'},
                                'title': {'type': 'string'},
                                'content': {'type': 'string'},
                                'source_type': {'type': 'string'},
                                'source_url': {'type': 'string'},
                                'tags': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                },
                                'timestamp': {'type': 'string'},
                            },
                        },
                    },
                    'topic_map': {'type': 'object'},
                    'quality_score': {'type': ['number', 'null']},
                },
            },
        }

        self.validators: Dict[str, Draft7Validator] = {}
        if JSONVALIDATOR_AVAILABLE:
            self.validators = {
                key: Draft7Validator(schema)
                for key, schema in self.schemas.items()
            }
        else:
            logger.warning("jsonschema not available – structural validation skipped")

    def validate(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payloads and return sanitised copy."""

        if not isinstance(outputs, dict):
            raise ValueError("Outputs must be a dictionary")

        sanitised: Dict[str, Any] = {}

        for key in self.schemas.keys():
            section = outputs.get(key)
            if section is None:
                raise ValueError(f"Missing output section '{key}'")

            if JSONVALIDATOR_AVAILABLE:
                validator = self.validators[key]
                errors = sorted(validator.iter_errors(section), key=lambda e: e.path)
                if errors:
                    message = "; ".join(f"{list(error.path)}: {error.message}" for error in errors)
                    raise ValueError(f"Validation failed for '{key}': {message}")

            sanitised[key] = self._clean_section(section)

        return sanitised

    @staticmethod
    def _clean_section(section: Any) -> Any:
        """Recursively strip whitespace and normalise simple types."""

        if isinstance(section, str):
            return section.strip()

        if isinstance(section, list):
            return [StructuredOutputValidator._clean_section(item) for item in section]

        if isinstance(section, dict):
            return {
                key: StructuredOutputValidator._clean_section(value)
                for key, value in section.items()
            }

        return section


class KnowledgeStore:
    """Persist knowledge items with optional Mem0 ingestion."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.index_dir = base_path / 'data' / 'knowledge_index'
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.mem0_enabled = False
        self.memory: Memory | None = None

        if MEM0_AVAILABLE:
            try:
                self.memory = Memory()
                self.mem0_enabled = True
            except Exception as exc:  # noqa: BLE001
                logger.warning("Mem0 initialisation failed: %s", exc)

    def ingest(
        self,
        domain_key: str,
        knowledge_items: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Ingest knowledge items, deduplicating via index state."""

        index = self._load_index(domain_key)
        new_items: List[Dict[str, Any]] = []

        for item in knowledge_items:
            identifier = item.get('id') or self._generate_identifier(item)
            if identifier in index:
                continue

            item['id'] = identifier
            index.add(identifier)
            new_items.append(item)

        user_id = f"domain_{domain_key}"
        ingested = 0
        mem0_failures: List[str] = []

        if self.mem0_enabled and self.memory:
            for item in new_items:
                try:
                    self.memory.add(
                        item.get('content', ''),
                        user_id=user_id,
                        metadata={
                            'id': item['id'],
                            'title': item.get('title'),
                            'source_type': item.get('source_type'),
                            'source_url': item.get('source_url'),
                            'tags': ','.join(item.get('tags', [])),
                            'timestamp': item.get('timestamp'),
                            'domain': domain_key,
                            'pipeline_quality_score': metadata.get('synthesizer', {}).get('quality_score'),
                        },
                    )
                    ingested += 1
                except Exception as exc:  # noqa: BLE001
                    logger.error("Mem0 ingestion failed for %s: %s", item['id'], exc)
                    mem0_failures.append(item['id'])

        self._save_index(domain_key, index)

        return {
            'attempted': len(knowledge_items),
            'deduplicated': len(knowledge_items) - len(new_items),
            'queued': len(new_items),
            'mem0_ingested': ingested,
            'mem0_failed': mem0_failures,
        }

    def _load_index(self, domain_key: str) -> set[str]:
        index_file = self.index_dir / f'{domain_key}.json'
        if not index_file.exists():
            return set()

        try:
            with open(index_file, 'r') as fh:
                return set(json.load(fh))
        except json.JSONDecodeError:
            logger.warning("Corrupted index for %s – rebuilding", domain_key)
            return set()

    def _save_index(self, domain_key: str, index: set[str]) -> None:
        index_file = self.index_dir / f'{domain_key}.json'
        with open(index_file, 'w') as fh:
            json.dump(sorted(index), fh, indent=2)

    @staticmethod
    def _generate_identifier(item: Dict[str, Any]) -> str:
        basis = json.dumps(
            {
                'title': item.get('title'),
                'source_url': item.get('source_url'),
                'content': item.get('content'),
            },
            sort_keys=True,
            default=str,
        )
        return sha256(basis.encode('utf-8')).hexdigest()


class KnowledgePipeline:
    """Coordinate collection, validation, and ingestion."""

    def __init__(self, base_path: Path = BASE_PATH) -> None:
        self.base_path = base_path
        self.validator = StructuredOutputValidator()
        self.store = KnowledgeStore(base_path)
        self.runs_dir = base_path / 'data' / 'pipeline_runs'
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def run(self, domain_key: str) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        run_id = start_time.strftime('%Y%m%d_%H%M%S')
        run_dir = self._prepare_run_dir(domain_key, run_id)

        logger.info("Starting pipeline run %s for %s", run_id, domain_key)

        crew = DataCollectionCrew(domain_key)

        try:
            run_summary = crew.run_collection()
        except OutputValidationError as exc:
            logger.error("Crew execution failed: %s", exc)
            raise

        raw_outputs = run_summary.get('outputs', {})
        validated_outputs = self.validator.validate(raw_outputs)

        self._persist_artifacts(run_dir, run_summary, validated_outputs)

        knowledge_items = validated_outputs['synthesizer'].get('knowledge_base', [])
        ingestion_result = self.store.ingest(domain_key, knowledge_items, validated_outputs)

        final_summary = {
            'run_id': run_id,
            'domain_key': domain_key,
            'started_at': start_time.isoformat(),
            'artifact_dir': str(run_dir),
            'ingestion': ingestion_result,
            'mem0_enabled': self.store.mem0_enabled,
        }

        summary_path = run_dir / 'pipeline_summary.json'
        with open(summary_path, 'w') as fh:
            json.dump(final_summary, fh, indent=2)

        logger.info("Pipeline complete for %s – %s new items", domain_key, ingestion_result['queued'])
        return final_summary

    def _prepare_run_dir(self, domain_key: str, run_id: str) -> Path:
        run_dir = self.runs_dir / domain_key / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _persist_artifacts(
        self,
        run_dir: Path,
        run_summary: Dict[str, Any],
        validated_outputs: Dict[str, Any],
    ) -> None:
        raw_file = run_dir / 'raw_run_summary.json'
        with open(raw_file, 'w') as fh:
            json.dump(run_summary, fh, indent=2)

        outputs_file = run_dir / 'validated_outputs.json'
        with open(outputs_file, 'w') as fh:
            json.dump(validated_outputs, fh, indent=2)

        # Persist source-aligned excerpts for transparency
        for key, section in validated_outputs.items():
            section_file = run_dir / f'{key}.json'
            with open(section_file, 'w') as fh:
                json.dump(section, fh, indent=2)


def run_cli() -> None:
    parser = argparse.ArgumentParser(
        description='Autonomous knowledge curation pipeline',
    )
    parser.add_argument('domain', help='Domain key to process')

    args = parser.parse_args()

    pipeline = KnowledgePipeline()
    result = pipeline.run(args.domain)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run_cli()


