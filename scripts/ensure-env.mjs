import { copyFileSync, existsSync, readFileSync, appendFileSync, writeFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

function envValue(content, key) {
  const m = content.match(new RegExp(`^${key}=(.*)$`, 'm'))
  return m ? m[1].trim() : null
}

function upsertEnvKey(filePath, key, value) {
  if (!existsSync(filePath)) return false
  let content = readFileSync(filePath, 'utf8')
  const re = new RegExp(`^${key}=.*$`, 'm')
  if (re.test(content)) {
    content = content.replace(re, `${key}=${value}`)
  } else {
    content += `\n${key}=${value}\n`
  }
  writeFileSync(filePath, content)
  return true
}

for (const dir of ['siege', 'pays/bresil', 'pays/equateur', 'pays/colombie']) {
  const envPath = join(root, dir, '.env')
  const examplePath = join(root, dir, '.env.example')
  if (!existsSync(envPath) && existsSync(examplePath)) {
    copyFileSync(examplePath, envPath)
    console.log(`[start] Cree ${dir}/.env depuis .env.example`)
  }
}

const rootEnvPath = join(root, '.env')
if (existsSync(rootEnvPath)) {
  const rootContent = readFileSync(rootEnvPath, 'utf8')
  const mysqlUrl = envValue(rootContent, 'MYSQL_URL')
  if (mysqlUrl) {
    for (const dir of ['pays/bresil', 'pays/equateur', 'pays/colombie', 'siege']) {
      const envPath = join(root, dir, '.env')
      if (existsSync(envPath)) {
        let content = readFileSync(envPath, 'utf8')
        if (!/^MYSQL_URL=/m.test(content)) {
          appendFileSync(envPath, `\nMYSQL_URL=${mysqlUrl}\n`)
          console.log(`[start] MYSQL_URL propage dans ${dir}/.env`)
        }
      }
    }
  }

  let discordUrl = envValue(rootContent, 'DISCORD_WEBHOOK_URL')
  if (!discordUrl) {
    for (const dir of ['siege', 'pays/bresil', 'pays/equateur', 'pays/colombie']) {
      const envPath = join(root, dir, '.env')
      if (existsSync(envPath)) {
        discordUrl = envValue(readFileSync(envPath, 'utf8'), 'DISCORD_WEBHOOK_URL')
        if (discordUrl) break
      }
    }
    if (discordUrl) {
      upsertEnvKey(rootEnvPath, 'DISCORD_WEBHOOK_URL', discordUrl)
      console.log('[start] DISCORD_WEBHOOK_URL propage dans .env racine')
    }
  }

  if (discordUrl) {
    for (const dir of ['siege', 'pays/bresil', 'pays/equateur', 'pays/colombie']) {
      const envPath = join(root, dir, '.env')
      if (upsertEnvKey(envPath, 'DISCORD_WEBHOOK_URL', discordUrl)) {
        console.log(`[start] DISCORD_WEBHOOK_URL synchronise dans ${dir}/.env`)
      }
    }
  }
}
