describe('Color Hunter', () => {
  beforeEach(() => {
    cy.visit('/color-hunter')
  })

  it('renders lobby and game UI elements', () => {
    cy.log('Teszt: Ellenőrzi a lobby és játék UI elemek megjelenését.')
    // Lobby
    cy.get('#lobby').should('exist').and('be.visible')
    cy.get('#generate-code').should('exist').and('be.visible')
    cy.get('#code-display').should('exist')
    cy.get('#join-code').should('exist')
    cy.get('#join-btn').should('exist')
    cy.get('#players-list').should('exist')
    cy.get('#start-game').should('exist')

    // Game board
    cy.get('#target-image').should('exist')
    cy.get('#choices-container').should('exist')
  })

  it('generates a room code when clicking the generate button', () => {
    cy.log('Teszt: Ellenőrzi, hogy a kód generálása működik és formailag érvényes kódot ad.')
    cy.get('#code-display').invoke('text').then((before) => {
      cy.get('#generate-code').click()
      cy.get('#code-display').invoke('text').should((text) => {
        const trimmed = (text || '').trim()
        expect(trimmed).to.not.equal((before || '').trim())
        // Expect at least a short code made of letters/numbers (len >=4)
        expect(trimmed.length).to.be.at.least(4)
        expect(/^[A-Z0-9-]+$/i.test(trimmed)).to.be.true
      })
    })
  })

  it('result pages render and include the result renderer', () => {
    cy.log('Teszt: Ellenőrzi az eredményoldalak megjelenését és a result renderer script jelenlétét.')
    // Correct page
    cy.visit('/color-hunter/correct-answer')
    cy.get('#result-players-list').should('exist')
    cy.get('script[src*="color-hunter-result.js"]').should('exist')

    // Wrong page
    cy.visit('/color-hunter/wrong-answer')
    cy.get('#result-players-list').should('exist')
    cy.get('script[src*="color-hunter-result.js"]').should('exist')
  })
})
