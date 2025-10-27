describe('Auth pages', () => {
  it('login page: inputs and link to registration', () => {
    cy.visit('/api/login')
    cy.get('[data-cy="login-username"]').should('be.visible').type('user1')
    cy.get('[data-cy="login-password"]').should('be.visible').type('pass123')
    cy.get('[data-cy="register-link"]').should('be.visible').click()
    cy.url().should('include', 'registration.html')
  })

  it('registration page: inputs and submit', () => {
    cy.visit('/api/register')
    cy.get('[data-cy="reg-username"]').should('be.visible').type('newuser')
    cy.get('[data-cy="reg-email"]').should('be.visible').type('a@b.com')
    cy.get('[data-cy="reg-password"]').type('pw12345')
    cy.get('[data-cy="reg-password2"]').type('pw12345')
    cy.get('[data-cy="reg-submit"]').should('be.visible')
  })
})