Rails.application.routes.draw do
  get 'search' => 'search#concepts'
  get 'welcome/index'
  root 'welcome#index'
end
