import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Mode } from '../types'

const mode = atom({ plugin: 'tempo', key: 'mode' } as const, 'off' as Mode)

const MODES: readonly Mode[] = ['off', 'go']
const LABEL: Record<Mode, string> = { off: 'off', go: 'autonomous' }

// autonomous 模式下，Sprin 每則訊息後面都附這段（他看不到、模型讀得到）；改字只改這裡。
// 不用 prompt.compose 加 system prompt 段落：Mac app 的 session 帶 sdk-preset，
// 中途加的段落進不了模型（2026-10-26 在 desktop 實測過）。
const GO_NOTE = `【Tempo：autonomous】Sprin 不想被問，能自己判斷的就做到底：
- 該列選項時直接採推薦項，一句話交代理由。
- 能自己測的自己驗，別叫他動手。
- 做不完的講清楚卡在哪，不留給下一個 agent。
- 機密、破壞性 Git（force-push／reset／discard）、付費、資料遺失、對外送出、push 到別人的 repo：照舊先問。`

// 切換當下留給模型的一句，讓進行中的對話馬上知道節奏換了。
const NOTE: Record<Mode, string> = {
  off: '【Tempo：off】autonomous 的規則不再適用，照平常的規則做。',
  go: GO_NOTE,
}

const USAGE = '用法：/tempo [off|autonomous]，不帶參數就在兩者之間切換。'

async function switchTo($: EngineInterface, next: Mode) {
  if ((await read($, mode)) === next) return

  await update($, mode, () => next)
  $.ui.status(next === 'go' ? 'Tempo：autonomous' : undefined)
  // append 被拒（這個 run 不讓 plugin 寫）也沒關係，下一則 prompt 照樣依 mode 附規則。
  await $.session
    .append({ message: { type: 'user', content: [{ type: 'text', text: NOTE[next] }] } })
    .catch(() => undefined)
}

function parse(args: string, current: Mode): Mode | null {
  const word = args.trim().toLowerCase()
  if (word === '') return current === 'go' ? 'off' : 'go'
  if (word === 'autonomous' || word === 'auto' || word === 'go') return 'go'
  if (word === 'off') return 'off'
  return null
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'tempo',
      description: '切換工作節奏：off 照常，autonomous 少問、自己驗、做到底',
      argumentHint: '[off|autonomous]',
      immediate: true,
    })
    // reload 後 $.state 還在，狀態列要跟著補回來。
    if ((await read($, mode)) === 'go') $.ui.status('Tempo：autonomous')

    return next(e)
  })

  on('command.run', { command: 'tempo' }, async ($, e) => {
    const target = parse(e.args, await read($, mode))
    if (target === null) return { text: USAGE }

    await switchTo($, target)

    return { text: `Tempo：${LABEL[target]}` }
  })

  // slash command（含 /tempo off 本身）不附；subagent 的 prompt 不走這個事件。
  on('prompt.submit', async ($, e, next) => {
    if (e.command || (await read($, mode)) !== 'go') return next(e)

    return next({ ...e, context: [...(e.context ?? []), GO_NOTE] })
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)

    const current = await read($, mode)
    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box>
        <Text dimColor>Tempo </Text>
        {MODES.map(m => (
          <Button
            key={m}
            label={LABEL[m]}
            variant={m === current ? 'primary' : 'secondary'}
            onPress={() => switchTo($, m)}
          />
        ))}
      </Box>
    )
  })
}
