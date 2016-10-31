class WelcomeController < ApplicationController
  def index
    if(params[:text])
      @query = Query.search(params[:text])
      render text: @query
    end
  end
end
