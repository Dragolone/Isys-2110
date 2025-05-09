const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080, path: '/updates' });

console.log('WebSocket server running at ws://localhost:8080/updates');

function randomValue(type) {
  if (type === 'energy') return Math.floor(Math.random() * 100);
  if (type === 'droid') return Math.floor(Math.random() * 100);
  if (type === 'facilities') return Math.floor(Math.random() * 100);
}

const types = ['energy', 'droid', 'facilities'];

wss.on('connection', function connection(ws) {
  console.log('Client connected');
  // 定时推送数据
  const interval = setInterval(() => {
    const type = types[Math.floor(Math.random() * types.length)];
    const value = randomValue(type);
    ws.send(JSON.stringify({ type, value }));
  }, 2000);

  ws.on('close', () => {
    clearInterval(interval);
    console.log('Client disconnected');
  });
}); 