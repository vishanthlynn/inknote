const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');

const fonts = {
    'default': 'Patrick Hand',
    'handlee': 'Handlee',
    'messy': 'Indie Flower',
    'cursive': 'Homemade Apple',
    'heading': 'Kalam Bold'
};

const colors = {
    'blue': '#0032B4',
    'black': '#141414',
    'red': '#C80000'
};

const renderPage = async (textLines, options = {}) => {
    const { style = 'default', color = 'blue', paper = 'blank', size = 28 } = options;
    const fontFamily = fonts[style] || fonts['default'];
    const inkColor = colors[color] || colors['blue'];
    const fontSize = size;
    const lineHeight = size * 1.6;

    // Launch reusable browser instance (in prod, use a pool)
    const browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();

    // Inject Fonts (Google Fonts URL for simplicity in MVP)
    const fontCss = `
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Handlee&family=Homemade+Apple&family=Indie+Flower&family=Kalam:wght@300;400;700&family=Patrick+Hand&family=Sacramento&family=Shadows+Into+Light&display=swap');
    `;

    // Paper Background CSS
    let bgCss = 'background-color: white;';
    if (paper === 'line') {
        bgCss = `
            background-color: white;
            background-image: linear-gradient(#e5e5f7 1px, transparent 1px);
            background-size: 100% ${lineHeight}px;
            background-position: 0 ${30}px;
            border-left: 1px solid #ff9999;
            padding-left: 60px;
        `;
    } else if (paper === 'grid') {
        bgCss = `
            background-color: white;
            background-image: linear-gradient(#e5e5f7 1px, transparent 1px), linear-gradient(90deg, #e5e5f7 1px, transparent 1px);
            background-size: ${lineHeight}px ${lineHeight}px;
        `;
    } else if (paper === 'dark') {
        bgCss = 'background-color: #1a1a1a; color: #ddd;';
    }

    // HTML Template
    const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            ${fontCss}
            body {
                margin: 0;
                padding: 40px;
                font-family: '${fontFamily}', cursive;
                font-size: ${fontSize}px;
                line-height: ${lineHeight}px;
                color: ${inkColor};
                ${bgCss}
                -webkit-font-smoothing: antialiased;
            }
            .line {
                display: block;
                /* Line-level drift/rotation for realism */
                transform-origin: center;
                /* Optimization: Combine transform in JS logic if needed */
            }
            .paper-container {
                width: 100%;
                height: 100%;
            }
        </style>
    </head>
    <body>
        <div class="paper-container">
            ${textLines.map(line => {
        // Random drift per line
        const rot = (Math.random() * 0.8) - 0.4; // -0.4deg to +0.4deg
        const xOff = Math.random() * 4; // 0 to 4px
        return `<div class="line" style="transform: rotate(${rot}deg) translateX(${xOff}px);">${line || '&nbsp;'}</div>`;
    }).join('')}
        </div>
    </body>
    </html>
    `;

    await page.setContent(htmlContent);

    // PDF Generation
    const filename = `rendered-${Date.now()}.pdf`;
    const outputPath = path.join(__dirname, '../outputs', filename);

    await page.pdf({
        path: outputPath,
        format: 'A4',
        printBackground: true,
        margin: { top: '0px', right: '0px', bottom: '0px', left: '0px' }
    });

    await browser.close();
    return outputPath;
};

module.exports = { renderPage };
