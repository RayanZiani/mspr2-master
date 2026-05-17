import { copyFileSync, existsSync, readFileSync, appendFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

function envValue(content, key) {
  const m = content.match(new RegExp(`^${key}=(.*)$`, 'm'))
  return m ? m[1].trim() : null
}

for (const dir of ['siege', 'pays/bresil', 'pays/equateur', 'pays/colombie']) {
  const envPath = join(root, dir, '.env')
  const examplePath = join(root, dir, '.env.example')
  if (!existsSync(envPath) && existsSync(examplePath)) {
    copyFileSync(examplePath, envPath)
    console.log(`[start] Créé ${dir}/.env depuis .env.example`)
  }
}

const siegeEnvPath = join(root, 'siege', '.env')
if (existsSync(siegeEnvPath)) {
  const siegeContent = readFileSync(siegeEnvPath, 'utf8')
  if (!/^MYSQL_URL=/m.test(siegeContent)) {
    const bresilEnvPath = join(root, 'pays/bresil', '.env')
    if (existsSync(bresilEnvPath)) {
      const dbUrl = envValue(readFileSync(bresilEnvPath, 'utf8'), 'DATABASE_URL')
      if (dbUrl) {
        appendFileSync(siegeEnvPath, `\nMYSQL_URL=${dbUrl}\n`)
        console.log('[start] MYSQL_URL ajouté dans siege/.env (depuis pays/bresil)')
      }
    }
  }
}
