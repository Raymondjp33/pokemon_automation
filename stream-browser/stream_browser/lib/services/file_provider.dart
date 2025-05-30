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
  DateTime now = DateTime.now();
  int screenIndex = 0;

  final List<String> logs = [
    'test',
    'test',
    'test',
  ];

  void addToLogs(String line) {
    logs.add(line);
    if (logs.length > 5) {
      logs.removeAt(0);
    }
  }

  void emitProcess() {
    socket!.emit('start_process');
  }

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

    socket!.on('process_output', (data) {
      addToLogs('Log: ${data['line']}');
      // Update UI with log line
    });

    socket!.on('process_complete', (data) {
      print('Process completed with code: ${data['code']}');
    });

    socket!.onDisconnect((_) => print('[Disconnected]'));

    socket!.connect();
  }

  late Timer timer;
  void startTimer() {
    timer = Timer.periodic(Duration(seconds: 1), (timer) {
      now = DateTime.now();

      if (now.second % 5 == 0) {
        // handleChangeScreenIndex();
      }
      notifyListeners();
    });
  }

  void handleChangeScreenIndex() {
    if (++screenIndex > 2) {
      screenIndex = 0;
    }
  }

  void updateVariables() {
    calculateSwitch1Variables();
    calculateSwitch2Variables();
  }

  //
  //        SWITCH 1
  //
  List<PokemonData> get switch1EggPokemon => (switch1Data?.pokemon ?? [])
      .where((e) => e.encounterMethod == 'egg')
      .toList();
  int switch1TotalShinies = 0;
  int switch1TotalEncounters = 0;
  double switch1AverageEncounters = 0;
  int switch1Encounters = 0;
  String shinyCounts = '';
  void calculateSwitch1Variables() {
    switch1TotalShinies = switch1EggPokemon.fold(
      0,
      (previousValue, element) =>
          previousValue + (element.catches ?? []).length,
    );
    switch1TotalEncounters = switch1EggPokemon.fold(
      0,
      (previousValue, element) => previousValue + (element.encounters ?? 0),
    );

    switch1AverageEncounters = switch1TotalEncounters / switch1TotalShinies;
    switch1Encounters = switch1CurrPokemon.encounters ?? 0;

    final shiniesCaught = switch1CurrPokemon.catches?.length ?? 0;
    final catchTarget = streamData?.switch1Target;

    if (catchTarget != null) {
      shinyCounts = '$shiniesCaught/$catchTarget';
    }

    notifyListeners();
  }

  //
  //        SWITCH 2
  //
  int switch2LegendaryShinies = 0;
  int switch2TotalDens = 0;
  int currentTotalDens = 0;
  double switch2AverageChecks = 0;
  int switch2Encounters = 0;

  PokemonData? switch2PokemonData(String pokemonName) {
    PokemonData? pokemonData;

    for (PokemonData pokemon in switch2Data?.pokemon ?? []) {
      if (pokemon.pokemon == pokemonName) {
        pokemonData = pokemon;
      }
    }
    return pokemonData;
  }

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
    currentTotalDens = switch2CurrPokemon.extraData?['total_dens'] ?? 0;
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
