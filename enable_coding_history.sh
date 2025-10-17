#!/bin/bash
# Script to safely re-enable coding history system after fix

echo "🔧 Coding History Re-enablement Script"
echo "======================================"
echo ""

# Check if .zshrc exists
if [ ! -f ~/.zshrc ]; then
    echo "❌ .zshrc not found. Creating one..."
    touch ~/.zshrc
fi

# Check if already enabled
if grep -q "coding_history_hooks_minimal.sh" ~/.zshrc; then
    echo "✅ Coding history hooks already enabled in .zshrc"
else
    echo "📝 Adding minimal coding history hooks to .zshrc..."
    echo "" >> ~/.zshrc
    echo "# Coding History - Minimal safe version (added $(date))" >> ~/.zshrc
    echo "source ~/AI-Workspace/scripts/coding_history_hooks_minimal.sh" >> ~/.zshrc
    echo "✅ Added to .zshrc"
fi

echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Open a new terminal window or tab"
echo "2. Test the commands:"
echo "   - ch_toggle      # Toggle capture on/off"
echo "   - ch_stats       # View statistics"
echo "   - ch_monitor     # Monitor activity"
echo ""
echo "3. To disable again, run: ch_off"
echo ""
echo "✅ Setup complete! The minimal hooks are now active."
echo ""
echo "Note: This is the SAFE minimal version that won't cause shell issues."