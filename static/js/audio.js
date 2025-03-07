(function() {
    let stopRecording, audioBlob, field;
    function startRecording() {
    if (navigator.mediaDevices) {
        console.log("getUserMedia supported.");
        const constraints = { audio: true };
        let chunks = [];

        navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            stopRecording = () => {
            mediaRecorder.stop();
            };

            mediaRecorder.onstop = (e) => {
                audioBlob = new Blob(chunks, { type: "audio/mp3" });
                console.log("recorder stopped");
                var url = (window.URL || window.webkitURL).createObjectURL(audioBlob);
                var link = document.getElementById("playRecord");
                link.src = url;
            };

            mediaRecorder.ondataavailable = (e) => {
            chunks.push(e.data);
            };
        })
        .catch((err) => {
            console.error(`The following error occurred: ${err}`);
        });
    }
    }


    function uploadAudio(blob, field){
        var formData = new FormData();
        var wavName = encodeURIComponent('audio_recording_' + new Date().getTime() + '.mp3');
        formData.append(field, blob, wavName);
        formData.append('csrfmiddlewaretoken', csrfToken);
        $.ajax({
            type: 'POST',
            url: '/upload_audio/' + lessonID + '/',
            data: formData,
            processData: false,
            contentType: false
        }).done(function(data) {
            location.reload();
        });
        console.log("uploading audio");
    }

    $(document).ready(function() {
    $('#id_image').on('change', function(event){
        var $imagePreview = $("#imagePreview");
        var files = event.target.files,
            file, field;
        if (files && files.length > 0) {
            file = files[0];
            var fileReader = new FileReader();
            fileReader.onload = function (event) {
                $imagePreview.attr('src', fileReader.result);
            };
            fileReader.readAsDataURL(file);
        }
    });
    $('#openRecordAudioModal').on('click touchstart', function(event) {
        $('.modal').modal();
        field = 'audio'
    });
    $('#openRecordEnglishAudioModal').on('click touchstart', function(event) {
        $('.modal').modal();
        field = 'english_audio'
    });
    $('#startRecord').on('click touchstart', function(event) {
        startRecording(event);
    });
    $('#stopRecord').on('click touchstart', function(event) {
        stopRecording(event);
    });

    $('#saveAudio').on('click touchstart', function(event) {
        uploadAudio(audioBlob, field);
    });

    });
})();
