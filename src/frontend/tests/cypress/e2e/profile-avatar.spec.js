describe('Profile avatar chooser', () => {
  it('displays 9 avatar options and back button', () => {
    cy.visit('/profile/avatar')
    cy.get('#avatar-grid').should('exist')
    cy.get('#avatar-grid .avatar-item').should('have.length', 9)
    cy.get('.back-btn').should('exist')
  })
})
