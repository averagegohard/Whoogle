require 'test_helper'

class SearchControllerTest < ActionDispatch::IntegrationTest
  test "should get concepts" do
    get search_concepts_url
    assert_response :success
  end

end
