(function() {
  var index;
  var sentences;
  var originalText;

  function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;
    // While there remain elements to shuffle...
    while (0 !== currentIndex) {
      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;

      // And swap it with the current element.
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
    }
    return array;
  }

  function getContainerHtml(character, index) {
    return '<div id="drop' + index + '" data-value="' + character + '" ' +
        'class="character-container">' +
        '<span class="glyphicon glyphicon-check hide" aria-hidden="true"></span>' +
        '<span class="glyphicon glyphicon-remove hide" aria-hidden="true"></span>' +
      '</div>';
  }

  function getCharacterHtml(character, index) {
    return '<div class="character-container">' +
        '<div id="drag' + index + '" data-value="' + character + '" class="character">' +
          character +
        '</div>' +
      '</div>';
  }

  function setCharacters(characters, selector, getHtmlCallBack) {
    var $container = $(selector);
    $container.html('');
    for (var i = 0; i < characters.length; i++) {
      var html = getHtmlCallBack(characters[i], i);
      $container.append(html);
    }
  }

  function newPlay(sentence) {
    setCharacters(sentence, '#main', getCharacterHtml);
    $('#startButton').removeAttr('disabled');
    $('#nextButton').attr('disabled', 'disabled');
    $('.character-container .glyphicon').addClass('hide');
    $('#originalText').html('');
  }

  function startPlay(sentence) {
    setCharacters(sentence, '#main', getContainerHtml);
    setCharacters(shuffle(sentence), '#sentence', getCharacterHtml);
    $('#startButton').attr('disabled', 'disabled');

    $('.character-container').droppable({
      hoverClass: "dash-border",
      drop: function(event, ui) {
        ui.draggable.detach().appendTo($(this));
        checkComplete();
      }
    });
    $('.character').draggable({
      helper: "clone",
      containment: "document"
    });
  }

  function checkComplete() {
    var containers = $('#main .character-container');
    for (var i = 0; i < containers.length; i++) {
      if ($(containers[i]).find('.character').length === 0) {
        return;
      }
    }
    $('#checkButton').removeAttr('disabled');
  }

  function checkResult() {
    var newClass;
    var succeed = true;
    var containers = $('#main .character-container');
    var successCharacters = [];
    var failedCharacters = [];

    containers.find('.glyphicon').addClass('hide');
    for (var i = 0; i < containers.length; i++) {
      $container = $(containers[i]);
      $character = $container.find('.character');
      if ($character.attr('data-value') === $container.attr('data-value')) {
        newClass = 'bg-success';
        $container.find('.glyphicon-check').removeClass('hide');
        successCharacters.push($container.attr('data-value'));
      } else {
        newClass = 'bg-danger';
        $container.find('.glyphicon-remove').removeClass('hide');
        succeed = false;
        failedCharacters.push($container.attr('data-value'));
      };
      $container.removeClass('bg-success');
      $container.removeClass('bg-danger');
      $container.addClass(newClass);
    }

    if (succeed) {
      $('#checkButton').attr('disabled', 'disabled');
      $('#nextButton').removeAttr('disabled');
    }
    increaseNumber(succeed);
    saveCharacters(successCharacters, failedCharacters);
  }

  function increaseNumber(succeed) {
    var glyphiconClass = succeed ? 'check' : 'remove';
    var selector = '.glyphicon-' + glyphiconClass + ' .check-result-number';
    var currentValue = parseInt($(selector).text());
    $(selector).html(currentValue + 1);
  }

  function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  function getPraise() {
    const praises = [
      'Great Job', 'Excellent', 'Fantastic', 'Wonderful', 'Super',
      'Marvelous', 'Brilliant', 'Awesome', 'Terrific', 'Well Done', 'Congratulations',
      'Amazing', 'Outstanding', 'Impressive', 'Keep it up', 'You Rock', 'Great Work',
      'Incredible', 'Fabulous', 'Remarkable', 'Respectable', 'Admirable', 'Superb',
      'Exceptional', 'Top Notch', 'First Class', 'Astonishing', 'Stellar', 'Phenomenal',
      'Unbelievable', 'Mind-blowing', 'Breathtaking', 'Jaw-dropping', 'Astounding',
      'Extraordinary', 'Unparalleled', 'Unmatched', 'Unrivaled', 'Supreme', 'Elite',
      'Champion', 'Heroic', 'Legendary', 'Epic', 'Majestic', 'Glorious', 'Radiant',
      'Dazzling', 'Shining', 'Brilliantly Done', 'Exquisitely Executed', 'Flawless',
      'Impeccable', 'Unforgettable', 'Triumphant', 'Victorious', 'Masterful',
      'Skillful', 'Talented', 'Gifted', 'Prodigious', 'Exceptional Talent','Mom','铁鞋'
    ];
    return shuffle(praises)[0];
  }

  function showDoneMessage() {
    var success = parseInt($('.glyphicon-check .check-result-number').text());
    var fail = parseInt($('.glyphicon-remove .check-result-number').text());
    var message;
    if (fail === 0) {
      showSuccessMessage();
      return;
    } else if (fail < success) {
      message = 'You are almost there! Try again!'
    } else {
      message = 'You can do better next time!'
    }
    showTryAgainMessage(success, fail, message);
  }

  function showSuccessMessage() {
    const DURATION = 1000;
    $('#main').html('<h1 id="done">' + getPraise() + '!</h1>');
    $('#done').css('text-shadow', "5px 5px 15px " + getRandomColor());
    $('#done').css('color', getRandomColor());
    $( "#done" ).animate({
      fontSize: "5em",
    }, DURATION);
  }

  function showTryAgainMessage(success, fail, message) {
    const DURATION = 3000;
    var html = '<h1 class="try-again">' +
      '<div class="text-success">Succss: ' + success + '</div>' +
      '<div class="text-danger">Fail: ' + fail + ' </div>' +
      '<div>' + message + '</div>' +
    '</h1>';
    $('#main').html(html);
    setTimeout(function() {
      reloadPlay();
    }, DURATION);
  }

  function reloadPlay() {
    if ($("form#characterForm").length){
      clearOldGame()
      $("#originalText").text(originalText);
      initPlay();
    } else {
      location.reload();
    }
  }

  function initPlay() {
    index = 0;
    sentences = JSON.parse(text);
  }

  function clearOldGame() {
    $(".ready-button").removeClass('hide');
    $(".action-buttons, .check-result").addClass('hide');
    $("#startButton").removeClass('hide');
    $("#startButton").removeAttr('disabled');
    $("#checkButton").attr('disabled', 'disabled');
    $("#nextButton").attr('disabled', 'disabled');
    $("#sentence").html('');
    $('#main').html('');
    $('.glyphicon-check .check-result-number').html('0');
    $('.glyphicon-remove .check-result-number').html('0');
  }

  function initFormSubmission() {
    $("form#characterForm").submit(function(event) {
        event.preventDefault(); // Prevent the default form submission
        var formData = new FormData(this);
        submitForm(formData);
    });

  }

  function submitForm(formData) {
    formData.append('csrfmiddlewaretoken', csrfToken);
    $.ajax({
      type: 'POST',
      url: '/practice/',
      data: formData,
      processData: false,
      contentType: false
    }).done(function(data) {
        clearOldGame();
        updateSentence(data);
        originalText = data.sentence;
        text = data.plain_text;
        initPlay();
    });
  }

  function saveCharacters(successCharacters, failedCharacters) {
    var formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrfToken);
    formData.append('successCharacters', JSON.stringify(successCharacters));
    formData.append('failedCharacters', JSON.stringify(failedCharacters));
    $.ajax({
      type: 'POST',
      url: '/save_characters/',
      data: formData,
      processData: false,
      contentType: false
    }).done(function(data) {
      var containers = $('#saved_characters .character-container');
      for (var i = 0; i < containers.length; i++) {
        $container = $(containers[i]);
        $character = $container.find('.saved_character');
        console.log($character);
        var saved_character = $character.html();
        if (successCharacters.includes(saved_character)) {
          var count = parseInt($container.find('.count-number').html());
          if (count >= 6 ) {
            // $container.html('');
            $container.parent().parent().html('');
          } else {
            $container.find('.count-number').html(count + 1);
          }
        } else if (failedCharacters.includes(saved_character)) {
          $container.find('.count-number').html("0");
        }
      }
    });
  }

  function updateSentence(data){
    $("#speech source").attr("src", data.speech);
    $("#speech")[0].load();
    $("#originalText").text(data.sentence);
    $("#pinyin").text(data.pinyin);
    $("#english").text(data.english);
  }

  $( document ).ready(function() {
    if ($("form#characterForm").length){
      initFormSubmission();
    } else {
      initPlay();
    }

    $(".ready-button").on('click touchstart', function(event) {
      $(this).addClass('hide');
      $(".action-buttons, .check-result").removeClass('hide');
      newPlay(sentences[index]);
    });

    $("#startButton").on('click touchstart', function(event) {
      if ($(this).attr('disabled') === 'disabled') {
        return;
      }
      startPlay(sentences[index]);

    });

    $("#checkButton").on('click touchstart', function(event) {
      if ($(this).attr('disabled') === 'disabled') {
        return;
      }
      checkResult();
    });

    $("#nextButton").on('click touchstart', function(event) {
      if ($(this).attr('disabled') === 'disabled') {
        return;
      }
      $('#sentence').html('');
      $('#main').html('');
      index++;
      if (index >= sentences.length) {
        showDoneMessage();
      } else {
        newPlay(sentences[index]);
      }
    });

    $(".saved_character").on('click touchstart', function(event) {
      var character = $(this).html();
      var count = $(this).attr('data-value');
      var formData = new FormData();
      formData.append('character', character);
      submitForm(formData);
    });
  });

})();
