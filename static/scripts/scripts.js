const BASE_URL = 'https://r14-warbler-p-n.herokuapp.com';
const $likeButton = $('.fa-thumbs-up');

$likeButton.on('click', async function (evt) {
  let $messageId = evt.target.closest('li').id;
  
  if($(this).hasClass('far')) {
    await axios.post(`${BASE_URL}/like/${$messageId}`);
  } else {
    await axios.post(`${BASE_URL}/unlike/${$messageId}`);
  };

  $(this).toggleClass('far fas');
});

