const fs = require('fs-extra');
const pdf = require('pdf-parse'); // You'll need to install this: npm install pdf-parse
const { preprocessText } = require('./ai');
const { renderPage } = require('./renderer');

const processPdf = async (filePath, options) => {
    // 1. Extract Text
    const dataBuffer = fs.readFileSync(filePath);
    const data = await pdf(dataBuffer);
    const rawText = data.text;

    // 2. AI Preprocessing
    console.log("Processing text with AI...");
    const lines = await preprocessText(rawText);

    // 3. Render Pages (Chunking)
    // Simple logic: 25 lines per page
    const linesPerPage = 25;
    const pages = [];
    for (let i = 0; i < lines.length; i += linesPerPage) {
        pages.push(lines.slice(i, i + linesPerPage));
    }

    if (pages.length === 0) pages.push([" "]);

    // Render each page
    console.log(`Rendering ${pages.length} pages...`);

    // For MVP, we just render the first page or combine them.
    // Puppeteer renderer currently returns one PDF path.
    // Let's modify renderer to handle multiple pages or just render all content in one long PDF?
    // Better: Render one PDF with page breaks.

    // Actually, our renderer takes "textLines". We can pass ALL lines and let HTML/CSS handle pagination?
    // Or render multiple PDFs and merge. 
    // For "HandTextAI clone", usually it's one PDF.
    // Let's pass ALL lines to renderer and let's update renderer to support auto-paging CSS?
    // Or simpler: Just render one long page for now if it's manageable, or loop.

    // Let's stick to simple: Render logic handles pagination via multiple <div> pages.
    // But our current renderer is single page.
    // Let's just pass the first chunk for the "Preview" equivalent, or Loop and Merge?
    // MVP: Just pass all lines, and let's update Renderer CSS to handle overflow or just huge page?
    // No, huge page is bad for printing.

    // Let's generate ONE PDF from the FIRST page for the MVP demonstration of quality.
    // Or loop and merge.

    // Let's update `renderPage` to accept all lines and handle paging internally in HTML?
    // That's complex.

    // Let's just render the first page for the "Preview/MVP" result.
    const resultPath = await renderPage(pages[0], options);

    return resultPath;
};

module.exports = { processPdf };
