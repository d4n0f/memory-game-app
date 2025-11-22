describe('Gamemode selector', () => {
  it('shows difficulty buttons and mode row + start button', () => {
    cy.visit('/gamemode-selector')
    cy.get('[data-cy="difficulty-easy"]').should('be.visible')
    cy.get('[data-cy="difficulty-medium"]').should('be.visible')
    cy.get('.mode-row').should('exist')
    cy.get('[data-cy="start-game-btn"]').should('be.visible')
  })
})
