# envault

> A CLI tool to securely manage and sync environment variables across projects using encrypted local storage.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize a vault for your project:**

```bash
envault init
```

**Add an environment variable:**

```bash
envault set API_KEY "your-secret-key"
```

**Retrieve a variable:**

```bash
envault get API_KEY
```

**Load all variables into your current shell session:**

```bash
eval $(envault load)
```

**Sync variables across projects:**

```bash
envault sync --project my-app
```

---

## How It Works

envault stores your environment variables in an AES-256 encrypted local vault. Each project gets its own isolated namespace, and variables can be shared or synced across projects using a master passphrase.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Pull requests are welcome! Please open an issue first to discuss any major changes.