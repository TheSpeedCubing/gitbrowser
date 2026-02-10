# gitbrowser

Web application to browse GitHub repositories and render Markdown files (can disable with query).  

## How to (As a User)

### URL Structure

- **Default**: `http://localhost:5011/<owner>/<repo>`
- **Specify branch**: `http://localhost:5011/<owner>/<repo>/tree/<branch>`

### Query Parameters

- `mdonly=0`: Show all files in the repository. By default, only `.md` (Markdown) files are displayed in the tree.
- `expand=1`: Automatically expand all directories in the file tree upon loading.


## How to (Deploy with Docker)

1. Clone this Repository:

   ```bash
   git clone https://github.com/TheSpeedCubing/gitbrowser.git
   cd gitbrowser
   ```

2. Add GitHub classic token in `.env`

    ```
    GITHUB_TOKEN=XXX
    ```

3. Start the container:

    ```bash
    sudo docker compose up -d
    ```

4. Access the site at:
   ```
   http://localhost:5011
   ```