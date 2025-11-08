# Contributing to AI Security Lab v4.0

Thank you for your interest in contributing to AI Security Lab! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Coding Standards](#coding-standards)
7. [Testing Guidelines](#testing-guidelines)
8. [Pull Request Process](#pull-request-process)
9. [Issue Reporting](#issue-reporting)
10. [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other conduct that would be considered unprofessional

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Git installed and configured
- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.11+
- A GitHub account

### First Time Setup

1. **Fork the Repository**
   ```bash
   # Visit https://github.com/shift7az/ai-security-lab-v4
   # Click "Fork" button
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-security-lab-v4.git
   cd ai-security-lab-v4
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/shift7az/ai-security-lab-v4.git
   ```

4. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### Backend Development

```bash
# Navigate to orchestrator
cd services/core/ai-orchestrator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python scripts/migrate.py

# Start development server
python main.py
```

### Frontend Development

```bash
# Navigate to dashboard
cd services/ui/dashboard

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

### Running with Docker

```bash
# Start all services
docker-compose -f docker/compose/docker-compose.yml up -d

# View logs
docker-compose logs -f
```

---

## Project Structure

```
ai-security-lab-v4/
├── services/
│   ├── core/
│   │   └── ai-orchestrator/      # Main backend service
│   │       ├── src/
│   │       │   ├── api/           # FastAPI endpoints
│   │       │   ├── core/          # Core business logic
│   │       │   ├── models/        # Pydantic models
│   │       │   ├── services/      # Service layer
│   │       │   └── utils/         # Utilities
│   │       ├── tests/             # Test files
│   │       └── migrations/        # Database migrations
│   ├── intelligence/
│   │   └── threat-detector/       # AI threat detection service
│   └── ui/
│       └── dashboard/             # Next.js frontend
│           ├── app/               # App router pages
│           ├── components/        # React components
│           ├── hooks/             # Custom hooks
│           └── lib/               # Utilities
├── config/                        # Configuration files
├── docs/                          # Documentation
├── scripts/                       # Utility scripts
└── docker/                        # Docker configurations
```

---

## Development Workflow

### Branch Naming Convention

Use descriptive branch names following this pattern:

```
feature/add-user-authentication
bugfix/fix-camera-connection
hotfix/security-vulnerability
docs/update-api-documentation
refactor/improve-database-queries
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: add new threat detection algorithm
fix: resolve camera stream timeout issue
docs: update deployment guide
style: format code with ruff
refactor: simplify database connection logic
test: add unit tests for auth service
chore: update dependencies
```

**Commit Message Structure:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples:**

```
feat(auth): implement JWT token refresh

- Add refresh endpoint to auth API
- Update token expiration logic
- Add tests for token refresh

Closes #123
```

```
fix(dashboard): resolve WebSocket reconnection issue

The WebSocket connection was not properly reconnecting after
network interruption. Added exponential backoff retry logic.

Fixes #456
```

---

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8 with additional rules

```python
# Use type hints
def process_frame(
    camera_id: str,
    frame_data: bytes,
    timestamp: datetime
) -> DetectionResult:
    """
    Process a camera frame for threat detection.
    
    Args:
        camera_id: Unique camera identifier
        frame_data: Raw frame bytes
        timestamp: Frame capture time
        
    Returns:
        DetectionResult with threats found
    """
    pass

# Use async/await for I/O operations
async def get_detections(
    db: DatabaseService,
    camera_id: str
) -> List[Detection]:
    """Fetch detections from database."""
    return await db.fetch_detections(camera_id)
```

**Linting:**

```bash
# Run Ruff for linting and formatting
ruff check .
ruff format .
```

### TypeScript (Frontend)

**Style Guide:** Standard TypeScript conventions

```typescript
// Use explicit types
interface CameraProps {
  cameraId: string;
  onDetection: (detection: Detection) => void;
}

// Prefer functional components with TypeScript
export function CameraCard({ cameraId, onDetection }: CameraProps) {
  const [status, setStatus] = useState<CameraStatus>('offline');
  
  // Use descriptive names
  const handleCameraError = (error: Error) => {
    console.error('Camera error:', error);
  };
  
  return <div>...</div>;
}
```

**Linting:**

```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

### Code Organization

- **Single Responsibility:** Each function/class should have one clear purpose
- **DRY Principle:** Don't repeat yourself
- **Clear Naming:** Use descriptive, self-documenting names
- **Comments:** Explain why, not what
- **Error Handling:** Always handle errors gracefully
- **Logging:** Use appropriate log levels

---

## Testing Guidelines

### Backend Tests (Pytest)

```python
# tests/test_auth_service.py
import pytest
from src.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_user_authentication(auth_service, test_user):
    """Test user can authenticate with correct credentials."""
    user = await auth_service.authenticate_user(
        username=test_user.username,
        password="test_password"
    )
    
    assert user is not None
    assert user.username == test_user.username
    assert user.role == test_user.role

@pytest.mark.asyncio
async def test_authentication_fails_with_wrong_password(auth_service, test_user):
    """Test authentication fails with incorrect password."""
    user = await auth_service.authenticate_user(
        username=test_user.username,
        password="wrong_password"
    )
    
    assert user is None
```

**Run Tests:**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth_service.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests (Jest/React Testing Library)

```typescript
// __tests__/CameraCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { CameraCard } from '@/components/cameras/CameraCard';

describe('CameraCard', () => {
  it('renders camera information correctly', () => {
    const camera = {
      id: 'cam-1',
      name: 'Front Entrance',
      status: 'online'
    };
    
    render(<CameraCard camera={camera} />);
    
    expect(screen.getByText('Front Entrance')).toBeInTheDocument();
    expect(screen.getByText('online')).toBeInTheDocument();
  });
  
  it('calls onDetection when detection occurs', () => {
    const handleDetection = jest.fn();
    const camera = { id: 'cam-1', name: 'Test', status: 'online' };
    
    render(
      <CameraCard camera={camera} onDetection={handleDetection} />
    );
    
    // Simulate detection
    fireEvent.click(screen.getByRole('button', { name: /detect/i }));
    
    expect(handleDetection).toHaveBeenCalled();
  });
});
```

**Run Tests:**

```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Generate coverage
npm test -- --coverage
```

---

## Pull Request Process

### Before Submitting

1. **Update from upstream**
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **Run tests**
   ```bash
   # Backend
   pytest
   
   # Frontend
   npm test
   ```

3. **Check code quality**
   ```bash
   # Backend
   ruff check .
   
   # Frontend
   npm run lint
   ```

4. **Update documentation** if needed

### Creating a Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Visit your fork on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

3. **PR Description Template**

   ```markdown
   ## Description
   Brief description of the changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing performed
   
   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests pass locally
   
   ## Related Issues
   Closes #123
   Related to #456
   ```

### PR Review Process

1. **Automated Checks:** CI/CD runs tests and linters
2. **Code Review:** Maintainer reviews code
3. **Feedback:** Address any requested changes
4. **Approval:** Maintainer approves PR
5. **Merge:** PR is merged to master

---

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Version: [e.g. 4.0.0]
 - Browser: [e.g. Chrome 120]

**Additional context**
Any other context about the problem.
```

### Feature Requests

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

---

## Documentation

### Documentation Guidelines

- Use clear, concise language
- Include code examples where appropriate
- Keep documentation up to date with code changes
- Use proper Markdown formatting
- Include diagrams for complex concepts

### Documentation Structure

```markdown
# Component Name

Brief description of the component.

## Purpose

What problem does this solve?

## Usage

```python
# Code example
from src.services import MyService

service = MyService()
result = service.do_something()
```

## API Reference

### Methods

#### `do_something(param1: str) -> Result`

Description of what the method does.

**Parameters:**
- `param1` (str): Description of parameter

**Returns:**
- `Result`: Description of return value

**Raises:**
- `ValueError`: When this happens

## Examples

### Example 1: Basic Usage

```python
# Example code
```

## See Also

- [Related Component](./related.md)
- [API Documentation](./api.md)
```

---

## Additional Resources

### Helpful Links

- [Project Documentation](https://github.com/shift7az/ai-security-lab-v4/tree/master/docs)
- [Issue Tracker](https://github.com/shift7az/ai-security-lab-v4/issues)
- [Discussions](https://github.com/shift7az/ai-security-lab-v4/discussions)

### Getting Help

- **Questions:** Use GitHub Discussions
- **Bugs:** Create an issue
- **Security:** Email security@example.com

### Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project website (if applicable)

---

## License

By contributing to AI Security Lab, you agree that your contributions will be licensed under the project's MIT License.

---

**Thank you for contributing to AI Security Lab!** 🚀

Your contributions help make this project better for everyone in the security community.
