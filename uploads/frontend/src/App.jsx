import React, {useState} from 'react';
export default function App(){
  const [resume, setResume] = useState('');
  const [role, setRole] = useState('Scrum Master');
  const [country, setCountry] = useState('FR');
  const [result, setResult] = useState(null);
  async function analyze(){
    const res = await fetch('/api/analyze', {
      method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({resume, role, country})
    });
    const data = await res.json();
    setResult(data);
  }
  return (<div style={{fontFamily:'Inter, system-ui',padding:20,background:'#0f172a',minHeight:'100vh',color:'#e6eef8'}}>
    <h1>Smart Learning Path — Live Prototype</h1>
    <div style={{marginTop:20}}>
      <textarea value={resume} onChange={e=>setResume(e.target.value)} rows={8} style={{width:'100%'}} placeholder="Paste resume text"></textarea>
      <input value={role} onChange={e=>setRole(e.target.value)} style={{marginTop:10,width:'100%'}} />
      <select value={country} onChange={e=>setCountry(e.target.value)} style={{marginTop:10}}>
        <option value="FR">France</option><option value="IN">India</option><option value="GLOBAL">Global</option>
      </select>
      <div style={{marginTop:10}}><button onClick={analyze} style={{padding:'8px 12px'}}>Analyze via AI</button></div>
      <pre style={{marginTop:12,background:'#0b1220',padding:12}}>{result?JSON.stringify(result,null,2):'No result yet'}</pre>
    </div>
  </div>);
}