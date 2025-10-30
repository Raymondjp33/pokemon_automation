// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pokemon_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PokemonData _$PokemonDataFromJson(Map<String, dynamic> json) => PokemonData(
      pokemon: (json['pokemon'] as List<dynamic>)
          .map((e) => PokemonModel.fromJson(e as Map<String, dynamic>?))
          .toList(),
      pokemonStats:
          StatsModel.fromJson(json['pokemonStats'] as Map<String, dynamic>?),
    );

Map<String, dynamic> _$PokemonDataToJson(PokemonData instance) =>
    <String, dynamic>{
      'pokemon': instance.pokemon.map((e) => e.toJson()).toList(),
      'pokemonStats': instance.pokemonStats.toJson(),
    };
