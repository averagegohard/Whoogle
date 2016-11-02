Rails.application.routes.draw do
  root 'welcome#index'
  get 'welcome/index'

  get 'search'  => 'welcome#search'
end
