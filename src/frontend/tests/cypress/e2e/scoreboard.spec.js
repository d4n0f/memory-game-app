describe('Scoreboard page', () => {
  it('shows scoreboard title and table', () => {
    cy.visit('/scoreboard')
    cy.get('.scoreboard-title').should('be.visible')
    cy.get('#scoreboard-table').should('exist')
  })
})
