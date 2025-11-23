describe('Scoreboard page', () => {
  it('shows scoreboard title and table', () => {
    cy.visit('/scoreboard')
    cy.get('.scoreboard-title').should('be.visible')
    cy.get('#list-container').should('exist')
  })
})
