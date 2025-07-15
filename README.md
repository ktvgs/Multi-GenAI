# Multi-GenAI
Additional features for customized requirements of mine with the working of generative AI.

import axios from 'axios';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = 'gemini-2.0-flash'; // or 'gemini-pro' depending on access
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1/models/${GEMINI_MODEL}:generateContent`;

export const sendToGemini = async (message: string) => {
  if (!GEMINI_API_KEY) {
    console.error('Missing GEMINI_API_KEY');
    return 'Server misconfiguration: missing API key';
  }

  const instructions =
    "Reply concisely in one short paragraph and, if applicable, list at most 5 bullet points.\n" +
    "At the end, include a 'Summary:' line with a one-sentence summary of your response.";

  const fullPrompt = `${instructions}\n\nUser: ${message}`;

  try {
    const response = await axios.post(
      `${GEMINI_API_URL}?key=${GEMINI_API_KEY}`,
      {
        contents: [
          {
            parts: [{ text: fullPrompt }]
          }
        ]
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    const text =
      response.data?.candidates?.[0]?.content?.parts?.[0]?.text ||
      'No response received from AI';

    return text;
  } catch (error: any) {
    console.error('Gemini API error:', error?.response?.data || error.message);
    return 'Error communicating with AI';
  }
};
