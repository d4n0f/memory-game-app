describe('Color Hunter page', () => {
  it('loads game UI and has multiplayer link', () => {
    cy.visit('/color-hunter')
    cy.get('#target-image').should('exist')
    cy.get('#choices-container').should('exist')
    cy.get('nav.multiplayer-link a').should('have.attr', 'href').and('include', '/color-hunter-multiplayer')
  })
})
