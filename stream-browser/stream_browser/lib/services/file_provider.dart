import 'dart:async';

import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;

import '../models/pokemon.model.dart';
import '../models/stream_data.model.dart';
import '../models/switch_data.model.dart';

class FileProvider with ChangeNotifier {
  FileProvider() {
    connectSocket();
    startTimer();
  }

  io.Socket? socket;

  SwitchData? switch1Data;
  SwitchData? switch2Data;
  StreamData? streamData;

  void connectSocket() {
    socket = io.io(
      'http://localhost:5050',
      io.OptionBuilder()
          .setTransports(['websocket'])
          .disableAutoConnect()
          .build(),
    );

    socket!.onConnect((_) {
      print('[Connected] to server');
      socket!.emit('init_connect');
    });

    socket!.on('stream_data', (data) {
      try {
        streamData = StreamData.fromJson(data);
        updateVariables();
        notifyListeners();
      } catch (e) {
        print('Error with data $e');
      }
    });

    socket!.on('switch1_data', (data) {
      try {
        switch1Data = SwitchData.fromJson(data);
        calculateSwitch1Variables();
        notifyListeners();
      } catch (e) {
        print('Error with data $e');
      }
    });

    socket!.on('switch2_data', (data) {
      try {
        switch2Data = SwitchData.fromJson(data);
        calculateSwitch2Variables();
        notifyListeners();
      } catch (e) {
        print('Error with data $e');
      }
    });

    socket!.onDisconnect((_) => print('[Disconnected]'));

    socket!.connect();
  }

  late Timer timer;
  void startTimer() {
    timer = Timer.periodic(Duration(seconds: 1), (timer) {
      notifyListeners();
    });
  }

  void updateVariables() {
    calculateSwitch1Variables();
    calculateSwitch2Variables();
  }

  //
  //        SWITCH 1
  //
  int switch1TotalShinies = 0;
  int switch1TotalEncounters = 0;
  double switch1AverageEncounters = 0;
  int switch1Encounters = 0;
  void calculateSwitch1Variables() {
    switch1TotalShinies = (switch1Data?.pokemon.length ?? 1) - 1;
    switch1TotalEncounters = (switch1Data?.pokemon ?? []).fold(
      0,
      (previousValue, element) => previousValue + (element.encounters ?? 0),
    );

    switch1AverageEncounters =
        switch1TotalEncounters / (switch1Data?.pokemon.length ?? 1);
    switch1Encounters = switch1CurrPokemon.encounters ?? 0;
    notifyListeners();
  }

  //
  //        SWITCH 2
  //
  int switch2LegendaryShinies = 0;
  int switch2TotalDens = 0;
  int totalDens = 0;
  double switch2AverageChecks = 0;
  int switch2Encounters = 0;

  void calculateSwitch2Variables() {
    switch2LegendaryShinies = (switch2Data?.pokemon.length ?? 1) - 1;
    switch2TotalDens = (switch2Data?.pokemon ?? []).fold(
      0,
      (previousValue, element) {
        if (element.extraData == null ||
            element.extraData?['total_dens'] is! int) {
          return previousValue + 0;
        }

        return previousValue + (element.extraData!['total_dens'] as int);
      },
    );

    List<PokemonData> denPokemon = (switch2Data?.pokemon ?? [])
        .where((e) => e.extraData?['total_dens'] != null)
        .toList();

    int totalEncounters = denPokemon.fold(
      0,
      (previousValue, element) => previousValue + (element.encounters ?? 0),
    );

    switch2AverageChecks = totalEncounters / denPokemon.length;
    switch2Encounters = switch2CurrPokemon.encounters ?? 0;
    notifyListeners();
  }

  PokemonData get switch1CurrPokemon =>
      switch1Data?.pokemon.firstWhere(
        (element) => element.pokemon == streamData?.switch1CurrentlyHunting,
        orElse: () => PokemonData.emptyPokemon,
      ) ??
      PokemonData.emptyPokemon;

  PokemonData get switch2CurrPokemon =>
      switch2Data?.pokemon.firstWhere(
        (element) => element.pokemon == streamData?.switch2CurrentlyHunting,
        orElse: () => PokemonData.emptyPokemon,
      ) ??
      PokemonData.emptyPokemon;
}
