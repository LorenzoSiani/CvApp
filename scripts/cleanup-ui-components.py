#!/usr/bin/env python3
"""
Script to identify and remove unused UI components from the frontend.
This helps reduce bundle size and clean up the codebase.
"""

import os
import re
import json
from pathlib import Path

def find_used_components():
    """Find all UI components that are actually used in the codebase."""
    used_components = set()
    
    # Define directories to search
    search_dirs = [
        Path('frontend/src'),
    ]
    
    # Pattern to find component imports
    import_pattern = r'from [\'"]\.\/components\/ui\/([^\'\"]+)[\'"]'
    destructured_pattern = r'import\s*{\s*([^}]+)\s*}\s*from\s*[\'"]\.\/components\/ui\/([^\'\"]+)[\'"]'
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for file_path in search_dir.rglob('*.js'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find direct imports
                matches = re.findall(import_pattern, content)
                for match in matches:
                    component_file = match.replace('.jsx', '').replace('.js', '')
                    used_components.add(component_file)
                
                # Find destructured imports
                matches = re.findall(destructured_pattern, content)
                for components, file_name in matches:
                    component_file = file_name.replace('.jsx', '').replace('.js', '')
                    used_components.add(component_file)
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return used_components

def get_all_ui_components():
    """Get all UI components in the components/ui directory."""
    ui_dir = Path('frontend/src/components/ui')
    
    if not ui_dir.exists():
        return set()
    
    components = set()
    for file_path in ui_dir.glob('*.jsx'):
        component_name = file_path.stem
        components.add(component_name)
    
    return components

def analyze_components():
    """Analyze component usage and identify unused ones."""
    used_components = find_used_components()
    all_components = get_all_ui_components()
    
    print("🔍 Component Usage Analysis")
    print("=" * 50)
    
    print(f"\n📊 Summary:")
    print(f"Total UI components: {len(all_components)}")
    print(f"Used components: {len(used_components)}")
    print(f"Unused components: {len(all_components - used_components)}")
    
    print(f"\n✅ Used Components ({len(used_components)}):")
    for component in sorted(used_components):
        print(f"  - {component}")
    
    unused = all_components - used_components
    if unused:
        print(f"\n❌ Unused Components ({len(unused)}):")
        for component in sorted(unused):
            print(f"  - {component}")
    
    return used_components, unused

def create_cleanup_script(unused_components):
    """Create a script to remove unused components."""
    if not unused_components:
        print("\n🎉 No unused components found!")
        return
    
    script_content = """#!/bin/bash
# Auto-generated script to remove unused UI components

echo "🧹 Cleaning up unused UI components..."

"""
    
    for component in sorted(unused_components):
        script_content += f'echo "Removing {component}.jsx"\n'
        script_content += f'rm -f frontend/src/components/ui/{component}.jsx\n'
    
    script_content += '\necho "✅ Cleanup completed!"\n'
    
    with open('scripts/remove-unused-components.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('scripts/remove-unused-components.sh', 0o755)
    
    print(f"\n📝 Created cleanup script: scripts/remove-unused-components.sh")
    print("Run with: ./scripts/remove-unused-components.sh")

def main():
    """Main function."""
    print("🚀 CVLTURE WordPress Manager - UI Component Cleanup")
    print("=" * 55)
    
    # Change to app directory
    if os.path.exists('/app'):
        os.chdir('/app')
    
    used_components, unused_components = analyze_components()
    
    # Create cleanup script
    os.makedirs('scripts', exist_ok=True)
    create_cleanup_script(unused_components)
    
    # Show component dependencies
    print(f"\n🔗 Component Dependencies:")
    print("The following components are essential for the WordPress Manager:")
    
    essential_components = [
        'button', 'card', 'input', 'label', 'tabs', 'badge', 
        'dialog', 'textarea', 'toast', 'toaster'
    ]
    
    for component in essential_components:
        status = "✅ Used" if component in used_components else "❌ Missing"
        print(f"  - {component}: {status}")
    
    print(f"\n💡 Recommendations:")
    if unused_components:
        print(f"  - Remove {len(unused_components)} unused components to reduce bundle size")
        print(f"  - Estimated space saved: ~{len(unused_components) * 2}KB")
    else:
        print("  - All components are being used efficiently!")
    
    print("  - Consider lazy loading components if bundle size becomes large")
    print("  - Regular cleanup helps maintain a clean codebase")

if __name__ == "__main__":
    main()