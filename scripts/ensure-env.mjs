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

const rootEnvPath = join(root, '.env')
if (existsSync(rootEnvPath)) {
  const rootContent = readFileSync(rootEnvPath, 'utf8')
  const mysqlUrl = envValue(rootContent, 'MYSQL_URL')
  if (mysqlUrl) {
    for (const dir of ['pays/bresil', 'pays/equateur', 'pays/colombie']) {
      const envPath = join(root, dir, '.env')
      if (existsSync(envPath)) {
        let content = readFileSync(envPath, 'utf8')
        if (!/^MYSQL_URL=/m.test(content)) {
          appendFileSync(envPath, `\nMYSQL_URL=${mysqlUrl}\n`)
          console.log(`[start] MYSQL_URL propagé dans ${dir}/.env`)
        }
      }
    }
  }
}
