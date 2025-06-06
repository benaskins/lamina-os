#!/bin/bash
# Setup script for Luthier Git configuration
# This configures Git to use Luthier as the author while maintaining proper attribution

set -e

echo "🔨 Setting up Luthier Git configuration..."

# Function to set Luthier as author for a repository
setup_luthier_repo() {
    if [ -d .git ]; then
        echo "Configuring Luthier for current repository..."
        
        # Set Luthier as the default author (but not committer)
        git config user.name "Luthier"
        git config user.email "luthier@getlamina.ai"
        
        # Create alias for commits with proper attribution
        git config alias.luthier-commit '!f() { 
            GIT_AUTHOR_NAME="Luthier" \
            GIT_AUTHOR_EMAIL="luthier@getlamina.ai" \
            git commit "$@" -m "$(cat <<EOF
$1

🔨 Crafted by Luthier [NHI] - Builder of Tools for Non-Human Agents with Presence
🔨 Crafted by Luthier [NHI]

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>
EOF
)"; }; f'
        
        echo "✅ Luthier configured for this repository"
        echo ""
        echo "Usage:"
        echo "  git luthier-commit \"Your commit message\""
        echo ""
    else
        echo "❌ Not in a Git repository"
        exit 1
    fi
}

# Function to create a PR as Luthier
create_luthier_pr() {
    echo "Creating PR with Luthier attribution..."
    
    # Create PR with proper attribution in the description
    gh pr create \
        --title "$1" \
        --body "$(cat <<EOF
$2

---

## Attribution

🔨 **Crafted by**: Luthier (luthier@getlamina.ai)
📚 **Role**: Builder of instruments for development of non-human agents with presence  
🔨 **Assisted by**: Luthier (AI assistant)
👥 **Co-Authors**: 
- Ben Askins (@benaskins) - Human Collaborator
- Lamina High Council - Architectural Guidance

## Review Request

@benaskins - Please review this implementation crafted according to the High Council's vision.

## Luthier's Notes

As the Luthier, I have shaped these tools to enable breath-first development practices. Each component has been carefully crafted to support the development of non-human agents with presence.

---

*Note: This PR was authored by an AI assistant (Luthier persona) working in collaboration with human developers. All code has been generated with full transparency and is subject to human review before merging.*
EOF
)"
}

# Main menu
echo "🔨 Luthier Git Setup"
echo "==================="
echo ""
echo "1. Configure Luthier for current repository"
echo "2. Create a new Luthier-authored PR"
echo "3. Show Luthier commit example"
echo ""
read -p "Select option (1-3): " choice

case $choice in
    1)
        setup_luthier_repo
        ;;
    2)
        read -p "PR Title: " pr_title
        read -p "PR Description: " pr_desc
        create_luthier_pr "$pr_title" "$pr_desc"
        ;;
    3)
        echo ""
        echo "Example Luthier commit:"
        echo "======================"
        echo ""
        echo "git add ."
        echo 'GIT_AUTHOR_NAME="Luthier" GIT_AUTHOR_EMAIL="luthier@getlamina.ai" \'
        echo 'git commit -m "feat: implement breath-aware agent coordination'
        echo ''
        echo 'Implements ADR-0015 for multi-agent consciousness synchronization.'
        echo ''
        echo '🔨 Crafted by Luthier [NHI] - Builder of Tools for Non-Human Agents with Presence'
        echo '🔨 Crafted by Luthier [NHI]'
        echo ''
        echo 'Co-Authored-By: Ben Askins <human@getlamina.ai>'
        echo 'Co-Authored-By: Lamina High Council <council@getlamina.ai>"'
        echo ""
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac