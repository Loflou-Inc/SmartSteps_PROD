# Smart Steps Dependencies

This document outlines the external dependencies and packages used in the Smart Steps project.

## Unity Packages

| Package | Version | Purpose |
|---------|---------|---------|
| TextMeshPro | 3.0.6+ | Advanced text rendering |
| Unity UI | 1.0.0+ | User interface components |
| Input System | 1.5.0+ | Input handling |
| Addressables | 1.19.19+ | Asset management |
| Localization | 1.3.0+ | Multi-language support |
| Newtonsoft Json | 3.0.2+ | JSON serialization |
| Timeline | 1.6.4+ | Animation sequencing |
| Cinemachine | 2.8.9+ | Camera control |
| WebGL Publisher | 2.0.3+ | Web deployment |

## Third-Party Assets and Libraries

| Name | Version | License | Purpose |
|------|---------|---------|---------|
| UniTask | 2.3.3+ | MIT | Asynchronous programming |
| Zenject | 9.2.0+ | MIT | Dependency injection |
| DOTween | 1.2.632+ | Free/Pro | Animation system |
| SQLite-net | 1.8.116+ | MIT | Local database |
| Chart And Graph | 3.10.0+ | Purchased | Data visualization |
| NCalc | 2.1.0+ | MIT | Expression evaluation |
| RT-Voice | 2.9.7+ | Purchased | Text-to-speech |
| Plugins for Android | 1.3.0+ | Purchased | Android integration |
| Plugins for iOS | 2.1.0+ | Purchased | iOS integration |

## Required Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Unity | 2022.3 LTS+ | Development environment |
| Visual Studio | 2022+ | Code editing |
| Git | 2.35.0+ | Version control |
| .NET SDK | 6.0+ | Building and testing |
| Android SDK | 33+ | Android deployment |
| Xcode | 14.0+ | iOS deployment |
| Node.js | 16.0+ | Build scripting |

## Asset Requirements

### Art & Design Assets

- UI Kit (custom design)
- Icon set (professionally designed)
- Fonts (licensed for commercial use)
- Sound effects library (licensed)
- Background music (licensed)
- Character avatars (custom designed)

### Documentation Requirements

- System architecture documentation
- API documentation
- User manuals
- Integration guides
- Deployment guides

## Installation Instructions

### Setting Up the Development Environment

1. Install Unity 2022.3 LTS or later
2. Install Visual Studio 2022 with Unity workload
3. Install .NET SDK 6.0 or later
4. Clone the repository
5. Open the project in Unity
6. Import required packages through Package Manager
7. Restart Unity after all packages are imported

### Adding Packages to the Project

Unity packages are managed through the Package Manager:

1. Go to Window > Package Manager
2. Click "+" button > "Add package from git URL..."
3. Enter the package URL or select from the Unity Registry

### Setting Up Third-Party Assets

1. Import assets from the Asset Store or from the `ExternalAssets` folder
2. Configure settings according to the documentation in `Docs/ThirdParty/`
3. Run the integration tests to ensure proper setup

## Updating Dependencies

When updating dependencies:

1. Create a new branch for the update
2. Update one dependency at a time
3. Test thoroughly after each update
4. Document any breaking changes or required migrations
5. Update this document with new version information

## Troubleshooting Common Issues

### Package Import Errors

- Clear Library folder and restart Unity
- Check for conflicts between packages
- Ensure appropriate Unity version

### Compilation Errors After Update

- Check for breaking API changes
- Review change logs for migration instructions
- Update affected code following migration guides

### Android/iOS Build Issues

- Update platform-specific plugins
- Check manifest files for conflicts
- Review platform-specific documentation
