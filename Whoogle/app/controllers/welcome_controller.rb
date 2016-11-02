include ActionView::Helpers::TextHelper
class WelcomeController < ApplicationController
  def index
  end
  
  def search
    if(params[:text])
      #file = File.open('whoogle/app/views/welcome/index.html.erb', 'rb')
      #render html: file.read
      @query = Query.search(params[:text])['concepts']
      result = simple_format('Whoogle Search')
      result += 'Analysis of Recent Tweets for Twitter User: ' + params[:text] +'
      
      '
      rank = 1
      for concept in @query
        result += rank.to_s+'. '+concept['text']+': '+concept['relevance']+'
        '
        rank += 1
      end
      render text: simple_format(result)
    end
  end
end
