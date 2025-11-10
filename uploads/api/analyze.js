import OpenAI from "openai";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export default async function handler(req, res){
  try{
    if(req.method !== 'POST') return res.status(405).json({error:'Method not allowed'});
    const { resume, role, country } = req.body;
    if(!resume || !role) return res.status(400).json({error:'resume and role required'});
    const prompt = `Extract a short skills list from this resume and compare with required skills for the role "${role}".
Resume:
${resume}

Respond JSON with keys: skills (array of skills found), match_percentage (0-100), missing_skills (array).`;
    const chat = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{role:'user', content: prompt}],
      max_tokens: 800,
    });
    const content = chat.choices?.[0]?.message?.content || chat.choices?.[0]?.message || '';
    // try to parse JSON from content
    let parsed = null;
    try{ parsed = JSON.parse(content); } catch(e){ parsed = { raw: content }; }
    return res.status(200).json({ ok:true, data: parsed });
  } catch(err){
    console.error(err);
    return res.status(500).json({ error: String(err) });
  }
}
