# 🤝 Contributing to LY-Merch

Thank you for your interest in contributing to LY-Merch! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## 📜 Code of Conduct

### Our Standards

- **Be respectful**: Treat everyone with respect and professionalism
- **Be inclusive**: Welcome contributors from all backgrounds and experience levels
- **Be constructive**: Provide helpful feedback and suggestions
- **Be collaborative**: Work together to improve the project

### Unacceptable Behavior

- Harassment, discrimination, or offensive language
- Trolling or insulting comments
- Publishing private information without permission
- Any conduct that could be considered inappropriate

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/ly-merch.git
   cd ly-merch
   ```

2. **Set up Development Environment**
   ```bash
   # Copy environment template
   cp .env.example .env

   # Start development services
   docker-compose up -d
   ```

3. **Verify Setup**
   ```bash
   # Test API
   curl http://localhost:8001/health

   # Test Frontend
   open http://localhost:8080
   ```

## 🔄 Development Workflow

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

Example: `feature/bulk-product-upload`

### Commit Message Format

Use the conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(api): add bulk product upload endpoint
fix(frontend): resolve CSV parsing error for special characters
docs(readme): update installation instructions
```

### Development Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Changes**
   ```bash
   # Backend tests
   cd api && python -m pytest

   # Frontend tests
   cd frontend && npm test

   # Integration tests
   cd scripts && python upload_csv_test.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(api): add bulk product upload endpoint"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🎯 Coding Standards

### Python (Backend)

#### Style Guide
- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use Black for code formatting

#### Code Structure
```python
# Good
def create_product(
    db: Session,
    product_data: ProductCreateRequest
) -> Optional[Product]:
    """Create a new product in the database.

    Args:
        db: Database session
        product_data: Product creation data

    Returns:
        Created product or None if failed
    """
    try:
        db_product = Product(**product_data.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create product: {e}")
        return None
```

#### Dependencies
- Use FastAPI for API endpoints
- SQLAlchemy for database operations
- Pydantic for data validation
- Add new dependencies to requirements.txt

### TypeScript/React (Frontend)

#### Style Guide
- Use TypeScript strictly
- Follow React best practices
- Use functional components with hooks
- Maximum line length: 80 characters

#### Component Structure
```tsx
// Good
interface ProductUploadProps {
  onUploadComplete: (results: UploadResults) => void;
  maxFileSize?: number;
}

export const ProductUpload: React.FC<ProductUploadProps> = ({
  onUploadComplete,
  maxFileSize = 10 * 1024 * 1024, // 10MB
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const handleUpload = useCallback(async (file: File) => {
    setIsUploading(true);
    try {
      const results = await uploadProductsAPI(file);
      onUploadComplete(results);
    } catch (error) {
      setErrors([error.message]);
    } finally {
      setIsUploading(false);
    }
  }, [onUploadComplete]);

  return (
    <div className="product-upload">
      {/* Component JSX */}
    </div>
  );
};
```

#### Dependencies
- Use React 18+ features
- Prefer built-in hooks over external libraries
- Add new dependencies to package.json

### Database

#### Migration Guidelines
- Always create reversible migrations
- Test migrations on sample data
- Include migration description
- Use descriptive table/column names

#### Schema Design
```sql
-- Good
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(500) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    brand VARCHAR(255),
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_product_type (product_type),
    INDEX idx_brand (brand),
    INDEX idx_created_at (created_at)
);
```

## 🧪 Testing Guidelines

### Backend Testing

#### Test Structure
```python
# tests/test_products.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_product():
    """Test product creation endpoint."""
    product_data = {
        "product_id": "TEST_001",
        "name": "Test Product",
        "product_type": "sneakers",
        "price": 99.99
    }

    response = client.post("/api/v1/products", json=product_data)

    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == "TEST_001"
    assert data["name"] == "Test Product"
```

#### Test Categories
- **Unit tests**: Test individual functions
- **Integration tests**: Test API endpoints
- **Database tests**: Test database operations

### Frontend Testing

#### Test Structure
```tsx
// __tests__/ProductUpload.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ProductUpload } from '../components/ProductUpload';

describe('ProductUpload', () => {
  it('should upload CSV file successfully', async () => {
    const mockOnUploadComplete = jest.fn();
    const file = new File(['name,type\nTest,sneakers'], 'test.csv', {
      type: 'text/csv'
    });

    render(<ProductUpload onUploadComplete={mockOnUploadComplete} />);

    const input = screen.getByLabelText(/choose file/i);
    fireEvent.change(input, { target: { files: [file] } });

    const uploadButton = screen.getByText(/upload/i);
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockOnUploadComplete).toHaveBeenCalled();
    });
  });
});
```

#### Test Categories
- **Component tests**: Test React components
- **Hook tests**: Test custom hooks
- **Integration tests**: Test component interactions

### Test Data

Use consistent test data:
```python
# Test fixtures
@pytest.fixture
def sample_product():
    return {
        "product_id": "TEST_001",
        "name": "Test Sneaker",
        "product_type": "sneakers",
        "brand": "Test Brand",
        "price": 99.99,
        "currency": "USD"
    }
```

## 📬 Pull Request Process

### Before Creating a PR

1. **Ensure tests pass**
   ```bash
   # Run all tests
   cd api && python -m pytest
   cd frontend && npm test
   ```

2. **Lint your code**
   ```bash
   # Python
   cd api && black app/ && flake8 app/

   # TypeScript
   cd frontend && npm run lint
   ```

3. **Update documentation**
   - Update README if needed
   - Add/update docstrings
   - Update API documentation

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by at least one maintainer
3. **Testing** on development environment
4. **Approval** from maintainer
5. **Merge** to main branch

## 🐛 Issue Reporting

### Bug Reports

Use this template for bug reports:

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
A clear and concise description of what actually happened.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91.0]
- Version: [e.g. v1.0.0]

## Additional Context
Add any other context about the problem here.
```

### Feature Requests

Use this template for feature requests:

```markdown
## Feature Description
A clear and concise description of what you want to happen.

## Problem Statement
A clear and concise description of what the problem is.

## Proposed Solution
Describe the solution you'd like.

## Alternative Solutions
Describe any alternative solutions you've considered.

## Additional Context
Add any other context or screenshots about the feature request here.
```

## 🏷️ Labels

We use these labels for issues and PRs:

- `bug` - Bug reports
- `enhancement` - Feature requests
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested
- `wontfix` - This will not be worked on

## 🚀 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Notes

Each release includes:
- Summary of changes
- New features
- Bug fixes
- Breaking changes (if any)
- Migration instructions (if needed)

## 💬 Communication

### Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code review and discussion

### Response Times

We aim for:
- Issues: Response within 48 hours
- PRs: Review within 72 hours
- Security issues: Response within 24 hours

## 🎉 Recognition

Contributors are recognized:
- In release notes
- In the project README
- Through GitHub's contributor statistics

Thank you for contributing to LY-Merch! 🙏