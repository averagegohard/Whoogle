Rails.application.routes.draw do
  # when a 'get search' is requested, what that really means is:
  # do the 'concepts' function in '/app/controllers/search_controller.rb'
  get 'search' => 'search#concepts'

  # set the homepage (located in /app/views/welcome/index.html.erb)
  get 'welcome/index'
  root 'welcome#index'
end
