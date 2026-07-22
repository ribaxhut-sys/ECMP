/**
 * Accessibility smoke checks (Sprint-10 RC1, P1 — warning mode in CI).
 * Uses axe-core against a representative presentational component.
 */
import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import axe from 'axe-core'
import { AsyncPanel } from './AsyncPanel'

async function runAxe(container: HTMLElement) {
  const results = await axe.run(container, {
    rules: {
      // jsdom lacks full layout/CSS; keep rules that are meaningful without a browser.
      'color-contrast': { enabled: false },
    },
  })
  return results.violations
}

describe('a11y smoke (AsyncPanel)', () => {
  it('loading state has no axe violations', async () => {
    const { container } = render(
      <AsyncPanel
        isLoading
        isError={false}
        isEmpty={false}
        emptyTitle="Empty"
        emptyMessage="Nothing here"
      >
        <p>Content</p>
      </AsyncPanel>,
    )
    expect(await runAxe(container)).toEqual([])
  })

  it('error state has no axe violations', async () => {
    const { container } = render(
      <AsyncPanel
        isLoading={false}
        isError
        errorTitle="Failed"
        errorMessage="Could not load"
        isEmpty={false}
        emptyTitle="Empty"
        emptyMessage="Nothing here"
      >
        <p>Content</p>
      </AsyncPanel>,
    )
    expect(await runAxe(container)).toEqual([])
  })

  it('empty state has no axe violations', async () => {
    const { container } = render(
      <AsyncPanel
        isLoading={false}
        isError={false}
        isEmpty
        emptyTitle="No cases"
        emptyMessage="Queue is empty"
      >
        <p>Content</p>
      </AsyncPanel>,
    )
    expect(await runAxe(container)).toEqual([])
  })
})