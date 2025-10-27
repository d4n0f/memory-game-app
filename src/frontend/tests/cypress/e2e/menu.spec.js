describe('Menu page', () => {
  it('shows scoreboard and lets you enter player name and start', () => {
    cy.visit('')
    cy.get('[data-cy="scoreboard"]').should('be.visible')
    cy.get('[data-cy="player-name"]').should('be.visible').type('Teszt Játékos')
    cy.get('[data-cy="start-btn"]').should('be.visible').click()
  })
})