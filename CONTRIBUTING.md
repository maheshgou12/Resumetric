# Contributing to CareerLens AI (Resumetric)

Thank you for your interest in contributing to **CareerLens AI**! We welcome contributions from the community to help make resume intelligence and career analytics accessible, transparent, and accurate.

---

## 🚀 Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/maheshgou12/Resumetric.git
cd Resumetric
```

### 2. Set Up Local Development
Follow the setup instructions in the [README.md](README.md):
- On Windows: run `.\start-dev.ps1` or double-click `start-dev.bat`.
- Cross-platform: start backend with `uvicorn main:app --reload` and frontend with `npm run dev`.

---

## 🧪 Testing Guidelines

Before submitting a Pull Request, verify that all backend tests and frontend builds pass cleanly:

```bash
# 1. Run Backend Pytest Suite
python -m pytest backend/tests -v

# 2. Build Frontend Production Assets
npm --prefix frontend run build
```

---

## 🌿 Branch and Commit Conventions

- Create feature branches with descriptive names:
  - `feat/feature-name` for new capabilities
  - `fix/bug-description` for bug fixes
  - `docs/doc-update` for documentation changes
- Use conventional commits format:
  - `feat: add cover letter tone selection`
  - `fix: resolve CORS header handling for edge preview domains`
  - `docs: update deployment keep-alive guide`

---

## 🔒 Security Policy

Please review our [SECURITY.md](SECURITY.md) for vulnerability disclosure procedures. Never commit credentials, private keys, or `.env` files.

---

## 📄 License

By contributing to CareerLens AI, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
