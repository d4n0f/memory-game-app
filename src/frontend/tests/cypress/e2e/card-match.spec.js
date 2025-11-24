describe('Card Match (Kártyapárosító)', () => {
  it('loads the card match board and info elements', () => {
    cy.visit('/card-match')
    cy.get('#game-board').should('exist')
    cy.get('#player-name-display').should('exist')
    cy.get('#score').should('exist')
    cy.get('#moves').should('exist')
  })
})
