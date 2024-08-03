$(document).ready(function() {
    $("#signup_btn").click(function() {
        // Impede que múltiplas animações se sobreponham
        $("#main, #loginform, #signupform").stop(true, true);

        // Move o #main para a posição da página de registro
        $("#main").animate({left: "22.5%"}, 100).animate({left: "30%"}, 200);

        // Esconde o #loginform
        $("#loginform").css("visibility", "hidden").animate({left: "25%"}, 400);

        // Move e mostra o #signupform
        $("#signupform").css("visibility", "visible").css("left", "17%").animate({left: "30%"}, 300);
    });

    $("#login_btn").click(function() {
        // Impede que múltiplas animações se sobreponham
        $("#main, #loginform, #signupform").stop(true, true);

        // Move o #main para a posição da página de login
        $("#main").animate({left: "77.5%"}, 100).animate({left: "70%"}, 200);

        // Esconde o #signupform
        $("#signupform").css("visibility", "hidden").animate({left: "75%"}, 400);

        // Move e mostra o #loginform
        $("#loginform").css("visibility", "visible").css("left", "83.5%").animate({left: "70%"}, 300);
    });
});
