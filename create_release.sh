#!/bin/bash
# Create release package for customer delivery

VERSION=${1:-v1.0.0}
RELEASE_DIR="releases/$VERSION"

echo "Creating release package: $VERSION"

# Create release directory
mkdir -p "$RELEASE_DIR"

# Copy application files
echo "Copying application files..."
cp -r app.py config.py extensions.py models/ modules/ templates/ static/ "$RELEASE_DIR/"

# Copy dependencies
echo "Copying dependencies..."
cp requirements.txt "$RELEASE_DIR/"

# Copy documentation
echo "Copying documentation..."
cp README.md "$RELEASE_DIR/"
cp -r docs/ "$RELEASE_DIR/"

# Copy install scripts
echo "Copying install scripts..."
cp install.bat start.bat .env.example "$RELEASE_DIR/"

# Copy tests (optional)
# cp -r tests/ "$RELEASE_DIR/"

# Create archive
echo "Creating ZIP archive..."
cd releases
zip -r "joy-vision-calculator-$VERSION.zip" "$VERSION/"
cd ..

echo "✅ Release package created: releases/joy-vision-calculator-$VERSION.zip"
echo ""
echo "Package contents:"
echo "- Application code"
echo "- Documentation (README, INSTALL_WINDOWS, INSTALL_UBUNTU, COMPARISON)"
echo "- Install scripts (install.bat, start.bat)"
echo "- Configuration example (.env.example)"
echo ""
echo "Next steps:"
echo "1. Test the package on clean Windows machine"
echo "2. Share with customer via Google Drive / Email / USB"
