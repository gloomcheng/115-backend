const basePath = import.meta.env.BASE_URL.replace(/\/+$/, '')

export function withBase(path: string): string {
  if (path.startsWith('#') || /^[a-z][a-z\d+.-]*:/i.test(path)) return path

  const relativePath = path.replace(/^\/+/, '')
  return relativePath ? `${basePath}/${relativePath}` : `${basePath}/`
}

export function withoutBase(pathname: string): string {
  if (!basePath || !pathname.startsWith(basePath)) return pathname
  return pathname.slice(basePath.length) || '/'
}
