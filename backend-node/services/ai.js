const OpenAI = require('openai');

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

const SYSTEM_PROMPT = `You are a text formatter. Take raw PDF text and output a JSON object with a key "lines" containing a list of clean lines (35–55 chars each).
Keep math equations, bullets, headings, and definitions.
Do not lose any content.
Break long paragraphs into multiple lines.
If there is a heading, make it a separate line.

Output JSON format:
{
  "lines": [
    "Heading Text",
    "Line 1 of content...",
    "Line 2 of content..."
  ]
}`;

const preprocessText = async (text) => {
    if (!text || !text.trim()) return [];

    try {
        const response = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                { role: "system", content: SYSTEM_PROMPT },
                { role: "user", content: `Format this text:\n\n${text.substring(0, 15000)}` }
            ],
            response_format: { type: "json_object" },
            temperature: 0.3
        });

        const content = response.choices[0].message.content;
        const data = JSON.parse(content);
        return data.lines || []; // Fallback to empty if structure mismatch

    } catch (error) {
        console.error("AI Preprocessing Error:", error);
        // Fallback: Simple splitting
        return simpleChunkText(text);
    }
};

const simpleChunkText = (text) => {
    const lines = [];
    const chunkSize = 50;
    const paragraphs = text.split('\n');

    for (let p of paragraphs) {
        p = p.trim();
        if (!p) continue;

        while (p.length > chunkSize) {
            let splitIdx = p.substring(0, chunkSize).lastIndexOf(' ');
            if (splitIdx === -1) splitIdx = chunkSize;
            lines.push(p.substring(0, splitIdx));
            p = p.substring(splitIdx).trim();
        }
        if (p) lines.push(p);
    }
    return lines;
};

module.exports = { preprocessText };
