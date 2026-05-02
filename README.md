# ChordPro Extractor API

Microserviço Python/FastAPI para extrair cifras em formato ChordPro a partir de PDF, imagem, PDF escaneado ou TXT. Ele foi pensado para ser consumido por um backend Spring Boot via `multipart/form-data`.

## O Que Ele Faz

- Recebe arquivos `PDF`, `PNG`, `JPG`, `JPEG`, `WEBP` e `TXT`.
- Tenta extrair texto selecionável de PDFs com PyMuPDF.
- Usa OCR com Tesseract quando o PDF não possui texto suficiente ou quando a entrada é imagem.
- Processa `TXT` como texto puro, preservando a posição aproximada dos acordes quando os espaços da cifra são mantidos.
- Agrupa tokens por linha e identifica linhas de acordes.
- Converte cifra no padrão visual tradicional para ChordPro.
- Retorna `confidence`, `status`, `warnings`, metadados e `requestId`.
- Possui limite de upload, limite de páginas, timeout de OCR, logs JSON e endpoints de health.

## Endpoints

### Health

```http
GET /health
GET /health/ready
```

### Extração ChordPro

```http
POST /api/v1/extractions/chordpro
Content-Type: multipart/form-data
```

Campo:

```text
file=<PDF, imagem ou TXT>
```

Resposta:

```json
{
  "requestId": "6e7128dc-6f4c-4eed-8778-3bdf515693ac",
  "status": "NEEDS_REVIEW",
  "sourceType": "OCR_IMAGE",
  "chordPro": "[E]Quando eu digo que deixei de te [B/D#]amar",
  "confidence": 0.72,
  "warnings": [
    "Imagem processada por OCR. Revise o resultado antes de salvar.",
    "A cifra convertida deve ser revisada manualmente."
  ],
  "metadata": {
    "filename": "musica.jpg",
    "mimeType": "image/jpeg",
    "fileSizeBytes": 381204,
    "pagesProcessed": 1,
    "tokenCount": 84,
    "lineCount": 12
  },
  "processingTimeMs": 1320
}
```

## Rodando Com Docker

Opcionalmente, crie o `.env` para sobrescrever os valores padrão:

```bash
cp .env.example .env
```

Suba o serviço:

```bash
docker compose up --build
```

Acesse:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Rodando Localmente

Instale as dependências de sistema:

### macOS

```bash
brew install tesseract tesseract-lang poppler
```

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-por tesseract-ocr-eng poppler-utils
```

Depois:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Exemplo cURL

```bash
curl -X POST "http://localhost:8000/api/v1/extractions/chordpro" \
  -H "X-Request-ID: teste-local-001" \
  -F "file=@/caminho/para/cifra.pdf"
```

## Exemplo Spring Boot

```java
MultipartBodyBuilder builder = new MultipartBodyBuilder();
builder.part("file", new FileSystemResource(filePath.toFile()));

WebClient client = WebClient.builder()
    .baseUrl("http://score-extractor-api:8000")
    .build();

Mono<ChordProExtractionResponse> response = client.post()
    .uri("/api/v1/extractions/chordpro")
    .header("X-Request-ID", requestId)
    .contentType(MediaType.MULTIPART_FORM_DATA)
    .body(BodyInserters.fromMultipartData(builder.build()))
    .retrieve()
    .bodyToMono(ChordProExtractionResponse.class);
```

## Configurações

As principais variáveis estão em `.env.example`:

```text
MAX_UPLOAD_SIZE_MB=20
MAX_PDF_PAGES=10
OCR_DPI=300
OCR_LANGUAGES=por+eng
OCR_TIMEOUT_SECONDS=45
REVIEW_CONFIDENCE_THRESHOLD=0.85
ALLOWED_MIME_TYPES_CSV=application/pdf,image/png,image/jpeg,image/webp,text/plain
ALLOWED_EXTENSIONS_CSV=.pdf,.png,.jpg,.jpeg,.webp,.txt
```

Para produção, ajuste `CORS_ALLOWED_ORIGINS_CSV` para a origem real do seu frontend/backend em vez de `*`.

## Status Da Extração

- `DONE`: extração confiável o suficiente para uso direto.
- `NEEDS_REVIEW`: resultado útil, mas deve ser revisado por uma pessoa.
- `FAILED`: não foi possível extrair conteúdo.

Como regra conservadora, saídas vindas de OCR tendem a retornar `NEEDS_REVIEW`.

## Qualidade Do ChordPro

O conversor usa a posição horizontal dos acordes para estimar o ponto de inserção na letra. Isso é melhor que encaixar apenas pela palavra mais próxima e cobre melhor casos como:

```text
        E                         B/D#
Quando eu digo que deixei de te amar
```

Saída esperada:

```text
[E]Quando eu digo que deixei de te [B/D#]amar
```

Mesmo assim, OCR e PDFs com layout irregular ainda podem exigir revisão humana.

Para arquivos `.txt`, prefira cifras com espaços preservados:

```text
        E                         B/D#
Quando eu digo que deixei de te amar
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

## Estrutura

```text
app/
  api/              rotas HTTP e dependências
  application/      orquestração do caso de uso
  domain/           modelos, enums e exceções
  infrastructure/   PyMuPDF, OCR, arquivos e conversão ChordPro
  presentation/     schemas de resposta
tests/
```
