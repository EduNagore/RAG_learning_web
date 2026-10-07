import type { BrowserContext, Route } from '@playwright/test';

export const SUPABASE_URL = 'http://127.0.0.1:54321';
export const AUTH_KEY = 'rma:supabase-auth';
export const PROGRESS_KEY = 'rma:progress:v1';

const b64 = (o: unknown) => Buffer.from(JSON.stringify(o)).toString('base64url');

export interface FakeUser {
  id: string;
  email: string;
}

/** Sesión con la forma que guarda supabase-js (JWT de pega con caducidad lejana). */
export function makeSession(user: FakeUser) {
  const exp = Math.floor(Date.now() / 1000) + 3600 * 24;
  const accessToken = `${b64({ alg: 'HS256', typ: 'JWT' })}.${b64({
    sub: user.id,
    email: user.email,
    role: 'authenticated',
    aud: 'authenticated',
    exp,
  })}.firma-de-prueba`;
  return {
    access_token: accessToken,
    refresh_token: 'refresh-de-prueba',
    token_type: 'bearer',
    expires_in: 3600 * 24,
    expires_at: exp,
    user: { id: user.id, email: user.email, aud: 'authenticated', role: 'authenticated' },
  };
}

/** Un «Supabase» en memoria: la tabla `progress` con RLS simulada y los endpoints de Auth que usamos. */
export class FakeSupabase {
  rows = new Map<string, { data: unknown; revision: number }>();
  otpEmails: string[] = [];
  verifyBodies: unknown[] = [];
  validCode = '123456';
  user: FakeUser = { id: 'user-1', email: 'ana@example.com' };
  offline = false;
  /** Peticiones a la tabla, para comprobar que no se sube de más. */
  tableCalls: string[] = [];

  async install(context: BrowserContext): Promise<void> {
    await context.route(`${SUPABASE_URL}/**`, (route) => this.handle(route));
  }

  private json(route: Route, status: number, body: unknown) {
    return route.fulfill({
      status,
      contentType: 'application/json',
      headers: { 'access-control-allow-origin': '*' },
      body: JSON.stringify(body),
    });
  }

  private async handle(route: Route): Promise<void> {
    const request = route.request();
    if (this.offline) return route.abort('failed');
    if (request.method() === 'OPTIONS') {
      return route.fulfill({
        status: 204,
        headers: {
          'access-control-allow-origin': '*',
          'access-control-allow-headers': '*',
          'access-control-allow-methods': 'GET,POST,PATCH,DELETE,OPTIONS',
        },
      });
    }
    const url = new URL(request.url());
    const body = request.postData() ? JSON.parse(request.postData()!) : undefined;

    if (url.pathname === '/auth/v1/otp') {
      this.otpEmails.push(body.email);
      return this.json(route, 200, {});
    }
    if (url.pathname === '/auth/v1/verify') {
      this.verifyBodies.push(body);
      if (body.token !== this.validCode) {
        return this.json(route, 403, {
          code: 403,
          error_code: 'otp_expired',
          msg: 'Token has expired or is invalid',
        });
      }
      return this.json(route, 200, makeSession(this.user));
    }
    if (url.pathname === '/auth/v1/user') {
      return this.json(route, 200, makeSession(this.user).user);
    }
    if (url.pathname === '/auth/v1/logout')
      return route.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*' } });

    if (url.pathname === '/rest/v1/progress') return this.table(route, url, body);
    return this.json(route, 404, { message: `sin simular: ${url.pathname}` });
  }

  private async table(
    route: Route,
    url: URL,
    body?: { user_id: string; data: unknown },
  ): Promise<void> {
    const request = route.request();
    const method = request.method();
    this.tableCalls.push(method);
    const uid = url.searchParams.get('user_id')?.replace('eq.', '') ?? body?.user_id ?? '';
    const wantsObject = (request.headers()['accept'] ?? '').includes('vnd.pgrst.object');

    if (method === 'GET') {
      const row = this.rows.get(uid);
      const rows = row ? [{ data: row.data, revision: row.revision }] : [];
      if (wantsObject) {
        return row
          ? this.json(route, 200, rows[0])
          : this.json(route, 406, { code: 'PGRST116', message: 'no rows' });
      }
      return this.json(route, 200, rows);
    }
    if (method === 'POST') {
      if (this.rows.has(body!.user_id)) {
        return this.json(route, 409, {
          code: '23505',
          message: 'duplicate key value violates unique constraint',
        });
      }
      this.rows.set(body!.user_id, { data: body!.data, revision: 1 });
      return this.json(route, 201, wantsObject ? { revision: 1 } : [{ revision: 1 }]);
    }
    if (method === 'PATCH') {
      const row = this.rows.get(uid);
      const revision = Number(url.searchParams.get('revision')?.replace('eq.', ''));
      if (!row || row.revision !== revision) return this.json(route, 200, []);
      row.data = body!.data;
      row.revision += 1;
      return this.json(route, 200, [{ revision: row.revision }]);
    }
    if (method === 'DELETE') {
      this.rows.delete(uid);
      return route.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*' } });
    }
    return this.json(route, 405, {});
  }
}
