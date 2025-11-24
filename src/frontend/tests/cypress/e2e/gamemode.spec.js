describe('Gamemode selector', () => {
  it('shows difficulty, modes and starts game', () => {
    cy.visit('/menu')
    cy.contains('Válaszd ki a nehézségi szintet').should('be.visible')
    cy.get('[data-cy="difficulty-easy"]').should('be.visible')
    cy.get('[data-cy="difficulty-hard"]').should('be.visible')
    cy.get('[data-cy="difficulty-medium"]').should('be.visible').click()
    cy.get('[data-cy="mode-row"]').should('be.visible')
    cy.get('[data-cy="mode-item"]').first().click()
    cy.get('[data-cy="start-game-btn"]').should('be.visible').click()
  })
})