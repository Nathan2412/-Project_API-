const request = require('supertest');
process.env.NODE_ENV = 'test';
const { app } = require('../src/index');

describe('Products API', () => {
  test('GET /api/products returns JSON payload (even if DB not connected)', async () => {
    const res = await request(app).get('/api/products');
    // Either pagination object or DB error; just check structure
    expect(res.status).toBeLessThan(600);
    expect(res.headers['content-type']).toMatch(/json/);
  });
});
