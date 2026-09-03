```
https://github.com/right9code/r9cn
```


```
/* Hide all GitHub headers, footers, toolbars, and file metadata */
header, 
footer, 
.AppHeader, 
#repository-container-header, 
.file-header, 
.js-file-header,
[data-testid="file-header"],
[class*="AuthorDisplayName"],
[class*="FileHeader"],
[class*="BoxHeader"] {
    display: none !important;
}

/* Hide GitHub's Latest Commit bar and commit attribution */
[class*="LatestCommit"],
[class*="CommitAttribution"],
[data-testid="latest-commit"],
[data-testid="latest-commit-details"] {
    display: none !important;
}

/* Hide GitHub's file view header (Preview/Code/Blame, file size, Raw/Download buttons) */
[class*="BlobViewHeader"],
[class*="BlobTabButtons"],
[class*="CodeSizeDetails"],
[class*="react-blob-header"] {
    display: none !important;
}

/* Remove borders, padding constraints, and expand markdown to 100% fullscreen */
main, 
.application-main, 
.repository-content, 
.markdown-body,
[class*="MarkdownViewer"],
[class*="BlobView"] {
    max-width: 100% !important;
    width: 100% !important;
    padding: 2rem !important;
    margin: 0 !important;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* Hide extra outer containers around the preview card */
.Box, 
[data-target="react-app.embeddedData"],
[class*="Box-"] {
    border: none !important;
    background: transparent !important;
}
```