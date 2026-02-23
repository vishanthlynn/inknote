const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs-extra');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Storage
const UPLOAD_DIR = path.join(__dirname, 'uploads');
const OUTPUT_DIR = path.join(__dirname, 'outputs');
fs.ensureDirSync(UPLOAD_DIR);
fs.ensureDirSync(OUTPUT_DIR);

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, UPLOAD_DIR),
    filename: (req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({ storage });

// Routes
app.get('/', (req, res) => {
    res.send('InkNotes Node.js Backend Running');
});

// Import Services (Placeholder for now)
const { processPdf } = require('./services/processor');

app.post('/upload', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

        const { style, color, paper, size } = req.query;

        // Start processing job (Sync for now, async later)
        const result = await processPdf(req.file.path, { style, color, paper, size: parseInt(size) || 28 });

        res.json({ status: 'completed', result_url: `/download/${path.basename(result)}` });

    } catch (error) {
        console.error("Upload Error:", error);
        res.status(500).json({ error: error.message, stack: error.stack });
    }
});

app.get('/download/:filename', (req, res) => {
    const filePath = path.join(OUTPUT_DIR, req.params.filename);
    if (fs.existsSync(filePath)) {
        res.sendFile(filePath);
    } else {
        res.status(404).json({ error: 'File not found' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
