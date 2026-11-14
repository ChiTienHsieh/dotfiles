import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'

const BAND = {
  plugin: 'tempo',
  component: 'AbovePrompt',
  props: {
    hasSurvey: false,
    isWorking: false,
    maxRows: 4,
    bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 4 },
    view: {},
  },
} as const

// 測試裡 plugin 底下沒有 engine：這幾個 hook 代替 engine 回答，並記下留給模型的 row。
async function start($: Engine, on: On) {
  const appended: string[] = []
  on('command.register', () => ({ value: { command: 'tempo' } }))
  on('ui.status', () => ({ value: undefined }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.append', (_, e, next) => {
    appended.push(e.message.type)

    return next(e)
  })
  on('prompt.submit', (_, e) => ({ text: e.text, context: e.context }))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  return appended
}

// 送一則 prompt，回傳模型會額外讀到幾段隱藏文字。
async function hiddenBlocks($: Engine, command?: { name: string; args: string }) {
  const result = await $.prompt.submit({
    text: 'hi',
    wait: false,
    origin: { kind: 'composer' },
    ...(command ? { command } : {}),
  })

  return result.context?.length ?? 0
}

function tempo($: Engine, args: string) {
  return $.command.run({
    command: 'tempo',
    args,
    origin: { kind: 'composer' },
    presentation: { isFullscreen: false, columns: 80 },
  })
}

test('band 在 terminal 與 desktop 都畫兩顆按鈕，按 autonomous 後 prompt 會附規則', async ($, on) => {
  const appended = await start($, on)

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    expect(await ui.find({ key: 'off' })).toBeDefined()
    expect(await ui.find({ key: 'go' })).toBeDefined()

    await ui.press({ key: 'go' })
    expect(await hiddenBlocks($)).toBe(1)

    await ui.press({ key: 'off' })
    expect(await hiddenBlocks($)).toBe(0)
    await ui.unmount()
  }

  // 每次真的切換都留一句給模型：terminal、desktop 各切兩次。
  expect(appended).toEqual(['user', 'user', 'user', 'user'])
})

test('按目前已經是的那顆不重複留言', async ($, on) => {
  const appended = await start($, on)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })

  await ui.press({ key: 'off' })
  await ui.press({ key: 'go' })
  await ui.press({ key: 'go' })
  expect(appended.length).toBe(1)
  await ui.unmount()
})

test('/tempo 切換、指定與錯誤參數', async ($, on) => {
  await start($, on)

  expect((await tempo($, '')).text).toBe('Tempo：autonomous')
  expect(await hiddenBlocks($)).toBe(1)

  expect((await tempo($, 'off')).text).toBe('Tempo：off')
  expect(await hiddenBlocks($)).toBe(0)

  for (const alias of ['autonomous', 'auto', 'go']) {
    await tempo($, 'off')
    expect((await tempo($, alias)).text).toBe('Tempo：autonomous')
  }
  expect((await tempo($, 'banana')).text).toContain('用法')
  expect((await tempo($, '放手')).text).toContain('用法')
  expect(await hiddenBlocks($)).toBe(1)
})

test('slash command 的 prompt 不附規則', async ($, on) => {
  await start($, on)
  await tempo($, 'go')

  expect(await hiddenBlocks($, { name: 'tempo', args: 'off' })).toBe(0)
})
