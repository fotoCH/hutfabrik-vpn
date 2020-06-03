var userlist;
var curruser;


function is_ascii(str) {
    return /^[\x00-\x7F]*$/.test(str);
}

function show_message(message, type, container){
  container = container || "#messagearea";
  var tpl = $("#tpl-message > div.alert");
  var msg = tpl.clone();
  msg.children(".text").html(message);
  msg.addClass("alert-"+type);
  $(container).append(msg);
}


function rebuild_userlist(){
  var tpl = $("#admin-tplarea tr.userentry");
  var area = $("#userlist");
  $.ajax({
    dataType: "json",
    url: "/list",
    contentType: 'application/json',
  }).done(function(data){
    area.html("");
    userlist = data.user;
    for (user of data.user){
      entry = tpl.clone();
      entry.children(".user").children("a").children(".username").html(user.name);
      entry.children(".desc").html(user.desc);
      entry.children(".admin").html(user.role);
      if (user.role == "admin") {
        entry.children(".isadm").children(".isadm_icon").removeClass("hidden");
      }
      entry.children(".user").children("a").attr("href", "javascript:edituser('"+user.name+"')");
      area.append(entry);
    }
  });
}

function edituser(user){
  $("#edituser-modal").modal("show");
  for (u of userlist){
    if (u.name==user){
      curruser = u;
    }
  }
  $("#euser").val(curruser.name);
  $("#edesc").val(curruser.desc);
  $("#epass").val(curruser.pass);
  if (curruser.role == "admin"){
    $('#eisadmin').prop('checked', true);
  } else {
    $('#eisadmin').prop('checked', false);
  }
}


$(document).ready(function(){

  // change password site
  $( "#pwform" ).submit(function( event ) {
    event.preventDefault();
    pw1 = $("#pass").val();
    pw2 = $("#pass2").val();
    if (pw1==""){
      show_message("Passwort darf nicht leer sein", "danger");
      return;
    }
    if (!is_ascii(pw1)){
      show_message("Passwort darf nur ASCII-Zeichen erhalten. <a class='alert-link' target='_blank' href='https://de.wikipedia.org/wiki/American_Standard_Code_for_Information_Interchange'>Hier</a> findest du eine Liste mit allen erlaubten Zeichen", "danger");
      return;
    }
    if (pw1 != pw2){
      show_message("Passwörter stimmen nicht überein", "danger");
      return;
    }

    $.post("/mypass", { pass:pw1 } ,function(data){
      if (data == "200"){
        show_message("Passwort erfolgreich geändert", "success");
      }
      else {
        show_message("Es ist ein Fehler aufgetreten. Bitte Admin kontaktieren.", "danger");
      }
    });
  });

  //
  // admin page
  //
  if (window.location.pathname == "/admin") {
    rebuild_userlist();

    // create new user
    $("#btn-newuser").click(function(){
      user = $("#nuser").val();
      pass = $("#npass").val();
      desc = $("#ndesc").val();
      isadm = $("#nisadmin").is(":checked");
      if (user==""){
        show_message("Benutzer darf nicht leer sein", "danger", "#messagearea-newuser");
        return;
      }if (pass==""){
        show_message("Passwort darf nicht leer sein", "danger", "#messagearea-newuser");
        return;
      }
      if (!is_ascii(pass)){
        show_message("Passwort darf nur ASCII-Zeichen erhalten. <a class='alert-link' target='_blank' href='https://de.wikipedia.org/wiki/American_Standard_Code_for_Information_Interchange'>Hier</a> findest du eine Liste mit allen erlaubten Zeichen", "danger", "#messagearea-newuser");
        return;
      }
      if (isadm) {
        user_role = "admin"
      }
      else {
        user_role = "user"
      }
      req_data = {
        user: user,
        pass: pass,
        desc: desc,
        role: user_role
      }
      $.post(
        "/newuser",
        req_data,
        function(data){
          if (data == "500"){
            show_message("Dieser Benutzer existiert bereits", "danger", "#messagearea-newuser");
            return;
          }
          if (data == "200"){
            rebuild_userlist();
            $("#newuser-modal").modal("hide");
            show_message("Benutzer <b>"+user+"</b> erfolgreich erstellt", "success");
          }
        }
      );
    });

    $("#btn-deluser").click(function(){
      if (confirm("Benutzer "+curruser.name+" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden")){
        $.post( "/deluser", { user: curruser.name }, function(data){
          rebuild_userlist();
          $("#edituser-modal").modal("hide");
          show_message("Benutzer <b>"+curruser.name+"</b> erfolgreich gelöscht", "success");
          curruser = {};
        });
      }
    });

    $("#btn-edituser").click(function(){
      user = $("#euser").val();
      pass = $("#epass").val();
      desc = $("#edesc").val();
      isadm = $("#eisadmin").is(":checked");
      if (pass==""){
        show_message("Passwort darf nicht leer sein", "danger", "#messagearea-edituser");
        return;
      }
      if (!is_ascii(pass)){
        show_message("Passwort darf nur ASCII-Zeichen erhalten. <a class='alert-link' target='_blank' href='https://de.wikipedia.org/wiki/American_Standard_Code_for_Information_Interchange'>Hier</a> findest du eine Liste mit allen erlaubten Zeichen", "danger", "#messagearea-edituser");
        return;
      }
      if (isadm) {
        user_role = "admin"
      }
      else {
        user_role = "user"
      }
      req_data = {
        user: user,
        pass: pass,
        desc: desc,
        role: user_role
      }
      $.post(
        "/pass",
        req_data,
        function(data){
          rebuild_userlist();
          $("#edituser-modal").modal("hide");
          show_message("Benutzer <b>"+curruser.name+"</b> erfolgreich geändert", "success");
          curruser = {};
        }
      );


    });



  }

});
